#!/usr/bin/env python3
"""BeanBotics Ticketing System - Flask-OpenAPI3 App with Automatic API Documentation"""
from flask import render_template, request, redirect, url_for
from flask_openapi3 import OpenAPI, Info
from flask_socketio import SocketIO, emit
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from database import db, init_db, create_ticket, get_all_tickets, get_ticket, add_comment, delete_ticket, seed_database

# OpenAPI Info
info = Info(title="BeanBotics Ticketing API", version="1.0.0", description="Real-time ticketing system for BeanBotics robotic coffee machines")

app = OpenAPI(__name__, info=info)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tickets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'beanbotics-ticketing-secret-key'

# Initialize extensions
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Pydantic Models for API Documentation and Validation

class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"

class TicketPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TicketCreate(BaseModel):
    title: str = Field(..., description="Ticket title describing the issue")
    description: Optional[str] = Field("", description="Detailed description of the problem")
    status: Optional[TicketStatus] = Field(TicketStatus.open, description="Ticket status")
    priority: Optional[TicketPriority] = Field(TicketPriority.medium, description="Priority level")

class TicketResponse(BaseModel):
    id: int = Field(..., description="Unique ticket identifier")
    title: str = Field(..., description="Ticket title")
    description: str = Field(..., description="Problem description")
    status: str = Field(..., description="Current status")
    priority: str = Field(..., description="Priority level")
    created_at: str = Field(..., description="Creation timestamp")
    comments: Optional[List[dict]] = Field([], description="Associated comments")

class TicketListResponse(BaseModel):
    tickets: List[TicketResponse] = Field(..., description="List of tickets")

class CommentCreate(BaseModel):
    author: str = Field(..., description="Comment author name")
    message: str = Field(..., description="Comment message content")

class CommentResponse(BaseModel):
    id: int = Field(..., description="Unique comment identifier")
    ticket_id: int = Field(..., description="Associated ticket ID")
    author: str = Field(..., description="Comment author")
    message: str = Field(..., description="Comment content")
    created_at: str = Field(..., description="Creation timestamp")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")

class TicketPathParam(BaseModel):
    ticket_id: int = Field(..., description="Ticket ID")

# Create tables within app context
with app.app_context():
    init_db()

# UI Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle form submission to create a new ticket
        ticket = create_ticket(
            title=request.form['title'],
            description=request.form.get('description', ''),
            status=request.form.get('status', 'open'),
            priority=request.form.get('priority', 'medium')
        )
        # Notify WebSocket clients of new ticket
        socketio.emit('ticket_created', {
            'event': 'ticket_created',
            'ticket': ticket,
            'message': f'New ticket created: {ticket["title"]}'
        })
        return redirect(url_for('index'))
    
    tickets = get_all_tickets()
    return render_template('index.html', tickets=tickets)

@app.route('/ticket/<int:ticket_id>', methods=['GET', 'POST'])
def ticket_detail(ticket_id):
    if request.method == 'POST':
        # Handle form submission to add a comment
        comment = add_comment(
            ticket_id=ticket_id,
            author=request.form['author'],
            message=request.form['message']
        )
        ticket = get_ticket(ticket_id)
        # Notify WebSocket clients of new comment
        socketio.emit('comment_created', {
            'event': 'comment_created',
            'comment': comment,
            'ticket_id': ticket_id,
            'ticket_title': ticket['title'],
            'message': f'New comment on ticket #{ticket_id}: {ticket["title"]}'
        })
        return redirect(url_for('ticket_detail', ticket_id=ticket_id))
    
    ticket = get_ticket(ticket_id)
    if not ticket:
        return "Ticket not found", 404
    return render_template('ticket_detail.html', ticket=ticket)

# API Routes with OpenAPI Documentation
@app.get('/api/tickets', responses={200: TicketListResponse})
def get_tickets():
    """Get all tickets
    
    Returns a list of all tickets in the system with their current status and details.
    """
    tickets = get_all_tickets()
    return {"tickets": tickets}

@app.post('/api/tickets', responses={201: TicketResponse, 400: ErrorResponse})
def create_ticket_api(body: TicketCreate):
    """Create a new support ticket
    
    Creates a new ticket in the BeanBotics support system. The system will automatically
    broadcast a real-time event to connected WebSocket clients.
    """
    try:
        ticket = create_ticket(
            title=body.title,
            description=body.description,
            status=body.status.value if isinstance(body.status, Enum) else body.status,
            priority=body.priority.value if isinstance(body.priority, Enum) else body.priority
        )
        # Notify WebSocket clients of new ticket via API
        socketio.emit('ticket_created', {
            'event': 'ticket_created',
            'ticket': ticket,
            'source': 'api',
            'message': f'New ticket created via API: {ticket["title"]}'
        })
        return ticket, 201
    except Exception as e:
        return {"error": str(e)}, 400

@app.get('/api/tickets/<int:ticket_id>', responses={200: TicketResponse, 404: ErrorResponse})
def get_ticket_api(path: TicketPathParam):
    """Get a specific ticket by ID
    
    Retrieves detailed information about a single ticket including all associated comments.
    """
    ticket = get_ticket(path.ticket_id)
    if not ticket:
        return {'error': 'Ticket not found'}, 404
    return ticket

@app.post('/api/tickets/<int:ticket_id>/comments', responses={201: CommentResponse, 400: ErrorResponse, 404: ErrorResponse})
def add_comment_api(path: TicketPathParam, body: CommentCreate):
    """Add a comment to an existing ticket
    
    Adds a new comment to the specified ticket. The system will broadcast a real-time
    event to connected WebSocket clients about the new comment.
    """
    try:
        comment = add_comment(
            ticket_id=path.ticket_id,
            author=body.author,
            message=body.message
        )
        ticket = get_ticket(path.ticket_id)
        if not ticket:
            return {'error': 'Ticket not found'}, 404
            
        # Notify WebSocket clients of new comment via API
        socketio.emit('comment_created', {
            'event': 'comment_created',
            'comment': comment,
            'ticket_id': path.ticket_id,
            'ticket_title': ticket['title'],
            'source': 'api',
            'message': f'New comment via API on ticket #{path.ticket_id}: {ticket["title"]}'
        })
        return comment, 201
    except Exception as e:
        return {"error": str(e)}, 400

@app.route('/ticket/<int:ticket_id>/delete', methods=['POST'])
def delete_ticket_route(ticket_id):
    ticket = get_ticket(ticket_id)  # Get ticket info before deletion
    if ticket and delete_ticket(ticket_id):
        # Notify WebSocket clients of ticket deletion
        socketio.emit('ticket_deleted', {
            'event': 'ticket_deleted',
            'ticket_id': ticket_id,
            'ticket_title': ticket['title'],
            'message': f'Ticket deleted: #{ticket_id} - {ticket["title"]}'
        })
        return redirect(url_for('index'))
    return "Ticket not found", 404

@app.route('/seed', methods=['POST'])
def seed_route():
    # Pass socketio to seed_database so it can emit events for each ticket/comment
    seed_database(socketio)
    return redirect(url_for('index'))

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    print(f'Agent connected: {request.sid}')
    emit('connected', {'message': 'Connected to BeanBotics Ticketing System'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Agent disconnected: {request.sid}')

@socketio.on('subscribe_to_tickets')
def handle_subscribe():
    """Allow agents to subscribe to ticket updates"""
    emit('subscribed', {'message': 'Subscribed to ticket updates'})

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000, host='0.0.0.0')
