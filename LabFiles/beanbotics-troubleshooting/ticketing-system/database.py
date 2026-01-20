#!/usr/bin/env python3
"""Database models for ticketing system using SQLAlchemy"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='open')
    priority = db.Column(db.String(50), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with cascade delete
    comments = db.relationship('Comment', backref='ticket', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'comments': [comment.to_dict() for comment in self.comments]
        }

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'author': self.author,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

def init_db():
    """Initialize database tables"""
    db.create_all()

def create_ticket(title, description='', status='open', priority='medium'):
    """Create a new ticket"""
    ticket = Ticket(
        title=title,
        description=description,
        status=status,
        priority=priority
    )
    db.session.add(ticket)
    db.session.commit()
    return ticket.to_dict()

def get_all_tickets():
    """Get all tickets ordered by creation date"""
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    return [ticket.to_dict() for ticket in tickets]

def get_ticket(ticket_id):
    """Get a specific ticket with its comments"""
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return None
    return ticket.to_dict()

def add_comment(ticket_id, author, message):
    """Add a comment to a ticket"""
    comment = Comment(
        ticket_id=ticket_id,
        author=author,
        message=message
    )
    db.session.add(comment)
    db.session.commit()
    return comment.to_dict()

def delete_ticket(ticket_id):
    """Delete a ticket and all its comments"""
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return False
    db.session.delete(ticket)  # Comments will be cascade deleted
    db.session.commit()
    return True

def seed_database(socketio=None):
    """Add one random BeanBotics support ticket to the database"""
    import random
    
    # Clear existing data
    Comment.query.delete()
    Ticket.query.delete()
    db.session.commit()
    
    # BeanBotics sample tickets
    sample_tickets = [
        {
            'title': 'BB-X1 Robotic Arm Not Responding',
            'description': 'The robotic arm on our BB-X1 unit froze mid-pour during the morning rush. Error code E003 showing on display. Customer was waiting for a latte when it happened.',
            'status': 'open',
            'priority': 'high'
        },
        {
            'title': 'Grinder Motor Overcurrent Issues',
            'description': 'Getting repeated grinder motor overcurrent warnings. Happens about 3-4 times per day, usually during busy periods. Unit auto-recovers but causes delays.',
            'status': 'in-progress',
            'priority': 'medium'
        },
        {
            'title': 'Facial Recognition Not Working',
            'description': 'Customer preference recognition system seems broken. Regular customers not being recognized, having to manually input their usual orders.',
            'status': 'open',
            'priority': 'low'
        },
        {
            'title': 'Boiler Temperature Inconsistent',
            'description': 'Water temperature fluctuating between 85-95°C instead of maintaining steady 93°C. Affecting espresso quality and customer complaints increasing.',
            'status': 'open',
            'priority': 'high'
        },
        {
            'title': 'Milk Frother Creating Poor Foam',
            'description': 'Steam wand not creating proper microfoam for cappuccinos and lattes. Foam is too thick and separates quickly. Checked steam pressure - seems normal.',
            'status': 'closed',
            'priority': 'medium'
        },
        {
            'title': 'Bean Hopper Sensor Malfunction',
            'description': 'System showing "insufficient beans" error even when hopper is full. Sensor seems to be stuck or miscalibrated.',
            'status': 'open',
            'priority': 'medium'
        }
    ]
    
    # Select one random ticket
    ticket_data = random.choice(sample_tickets)
    
    # Create the single random ticket
    ticket = Ticket(
        title=ticket_data['title'],
        description=ticket_data['description'],
        status=ticket_data['status'],
        priority=ticket_data['priority']
    )
    db.session.add(ticket)
    db.session.flush()  # Flush to get the ID
    db.session.commit()
    
    # Emit WebSocket event for the ticket created during seeding
    if socketio:
        socketio.emit('ticket_created', {
            'event': 'ticket_created',
            'ticket': ticket.to_dict(),
            'source': 'seed',
            'message': f'Random sample ticket created: {ticket.title}'
        })

