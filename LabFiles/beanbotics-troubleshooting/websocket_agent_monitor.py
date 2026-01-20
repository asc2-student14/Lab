#!/usr/bin/env python3
"""
WebSocket Agent Monitor for BeanBotics Ticketing System
Listens to ticketing events and responds using Fast-Agent MCP.
"""
import socketio
import asyncio
from datetime import datetime
from fast_agent.core.fastagent import FastAgent

# Configuration
SYSTEM_PROMPT = """You are a BeanBotics ticketing support agent.

Your task is to resolve tickets by:
- Adding comments to gather more information or assist the customer.
- Closing tickets when the issue has been fully resolved.

You MUST use the troubleshooting guides from MCP resources.
You MUST either comment on the ticket or close the ticket.
Comment or close the ticket as your final action.
Once you have taken your final action, state "Done".
Please use "BeanBotics AI" as your name."""

# Initialize FastAgent
fast = FastAgent("BeanBotics Ticketing Agent")

@fast.agent(instruction=SYSTEM_PROMPT, servers=["tickets"], use_history=False)
async def ticketing_agent(message):
    async with fast.run() as agent:
        await agent(message)

# Initialize Socket.IO client
sio = socketio.AsyncClient()

def print_event(event_name, data):
    """Print formatted event information"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] 🔔 {event_name.upper()}")
    print(f"  {data.get('message', 'No message')}")
    
    if 'ticket' in data:
        t = data['ticket']
        print(f"  #{t['id']}: {t['title']} [{t['status']}/{t['priority']}]")
    elif 'ticket_id' in data:
        title = f": {data['ticket_title']}" if 'ticket_title' in data else ""
        print(f"  #{data['ticket_id']}{title}")
    
    if 'comment' in data:
        c = data['comment']
        msg = c['message'][:80] + "..." if len(c['message']) > 80 else c['message']
        print(f"  {c['author']}: {msg}")
    
    print("-" * 50)

async def send_to_agent(prompt):
    """Send prompt to FastAgent and handle response"""
    print(f"🤖 Sending to FastAgent: {prompt}")
    try:
        response = await ticketing_agent(prompt)
        print(f"📝 FastAgent Response: {response}")
    except Exception as e:
        print(f"❌ FastAgent error: {e}")

# Socket.IO event handlers
@sio.event
async def connect():
    print("🟢 Connected to BeanBotics Ticketing System!")
    print("   Listening for events... Press Ctrl+C to disconnect")
    print("=" * 50)
    await sio.emit('subscribe_to_tickets')

@sio.event
async def disconnect():
    print("\n🔴 Disconnected from BeanBotics Ticketing System")

@sio.event
async def connected(data):
    print(f"✅ {data['message']}")

@sio.event
async def subscribed(data):
    print(f"✅ {data['message']}")

@sio.event
async def ticket_created(data):
    print_event('ticket_created', data)
    prompt = f"New ticket: {data['ticket']['title']}\nDescription: {data['ticket']['description']}"
    await send_to_agent(prompt)

@sio.event
async def comment_created(data):
    print_event('comment_created', data)
    # Skip AI comments to prevent loops
    if data['comment']['author'] == 'BeanBotics AI':
        print("🤖 Ignoring AI comment to prevent loop")
        return
    prompt = f"New comment on ticket #{data['ticket_id']}: {data['comment']['message']}"
    await send_to_agent(prompt)

@sio.event
async def ticket_deleted(data):
    print_event('ticket_deleted', data)

async def main():
    """Main function to start the WebSocket monitor"""
    print("🎫 BeanBotics WebSocket Agent Monitor")
    print("Connecting to localhost:5000...")
    
    try:
        await sio.connect('http://localhost:5000')
        await sio.wait()
    except KeyboardInterrupt:
        print("\n⏹️ Stopping monitor...")
        await sio.disconnect()
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("Ensure BeanBotics Ticketing System is running on localhost:5000")

if __name__ == '__main__':
    asyncio.run(main())
