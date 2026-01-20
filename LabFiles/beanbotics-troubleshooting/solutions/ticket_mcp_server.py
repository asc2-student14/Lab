#!/usr/bin/env python3
"""BeanBotics Ticketing MCP Server

This server provides tools for AI assistants to interact with the BeanBotics
ticketing system API. Agents can create tickets, add comments, and monitor
support requests for robotic coffee systems.
"""
from fastmcp import FastMCP
from fastmcp.server.context import Context
from typing import Dict, Any
import requests
from pathlib import Path

# Initialize the FastMCP server
mcp = FastMCP("BeanBoticsTicketing")

# Configuration
API_BASE_URL = "http://localhost:5000/api"
TROUBLESHOOTING_DIR = Path(__file__).parent / "troubleshooting"

def handle_api_error(response: requests.Response) -> str:
    """Handle API errors gracefully"""
    try:
        error_data = response.json()
        return f"API Error {response.status_code}: {error_data.get('error', 'Unknown error')}"
    except:
        return f"API Error {response.status_code}: {response.text}"

def load_troubleshooting_guide(filename: str) -> str:
    """Load a troubleshooting guide from markdown file"""
    try:
        guide_path = TROUBLESHOOTING_DIR / f"{filename}.md"
        return guide_path.read_text(encoding='utf-8') if guide_path.exists() else f"Guide not found: {filename}.md"
    except Exception as e:
        return f"Error loading guide {filename}: {str(e)}"

@mcp.tool()
def list_tickets() -> Dict[str, Any]:
    """Get all tickets from the BeanBotics ticketing system.
    
    Returns:
        Dictionary containing list of all tickets with their details
    """
    try:
        response = requests.get(f"{API_BASE_URL}/tickets")
        
        if response.status_code == 200:
            tickets = response.json()
            return {
                "tickets": tickets,
                "count": len(tickets),
                "summary": f"Found {len(tickets)} tickets in the system"
            }
        else:
            return {"error": handle_api_error(response)}
    
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to ticketing system. Is the server running on localhost:5000?"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def get_ticket(ticket_id: int) -> Dict[str, Any]:
    """Get detailed information about a specific ticket including comments.
    
    Args:
        ticket_id: The ID of the ticket to retrieve
    
    Returns:
        Dictionary containing ticket details and all comments
    """
    try:
        response = requests.get(f"{API_BASE_URL}/tickets/{ticket_id}")
        
        if response.status_code == 200:
            ticket = response.json()
            comment_count = len(ticket.get('comments', []))
            return {
                **ticket,
                "comment_count": comment_count,
                "summary": f"Ticket #{ticket_id}: {ticket.get('title', 'Unknown')} ({comment_count} comments)"
            }
        elif response.status_code == 404:
            return {"error": f"Ticket #{ticket_id} not found"}
        else:
            return {"error": handle_api_error(response)}
    
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to ticketing system. Is the server running on localhost:5000?"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def add_comment(
    ticket_id: int,
    author: str,
    message: str
) -> Dict[str, Any]:
    """Add a comment to an existing ticket.
    
    Args:
        ticket_id: The ID of the ticket to comment on
        author: Name of the person/agent adding the comment
        message: The comment message
    
    Returns:
        Dictionary containing the created comment information
    """
    try:
        payload = {
            "author": author,
            "message": message
        }
        
        response = requests.post(f"{API_BASE_URL}/tickets/{ticket_id}/comments", json=payload)
        
        if response.status_code == 201:
            comment = response.json()
            return {
                **comment,
                "summary": f"Added comment to ticket #{ticket_id} by {author}"
            }
        elif response.status_code == 404:
            return {"error": f"Ticket #{ticket_id} not found"}
        else:
            return {"error": handle_api_error(response)}
    
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to ticketing system. Is the server running on localhost:5000?"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def search_tickets_by_status(status: str) -> Dict[str, Any]:
    """Find tickets by their status.
    
    Args:
        status: Status to filter by (open, in-progress, closed)
    
    Returns:
        Dictionary containing filtered tickets
    """
    try:
        # Get all tickets and filter by status
        response = requests.get(f"{API_BASE_URL}/tickets")
        
        if response.status_code == 200:
            all_tickets = response.json()
            filtered_tickets = [t for t in all_tickets if t.get('status', '').lower() == status.lower()]
            
            return {
                "tickets": filtered_tickets,
                "count": len(filtered_tickets),
                "status": status,
                "summary": f"Found {len(filtered_tickets)} tickets with status '{status}'"
            }
        else:
            return {"error": handle_api_error(response)}
    
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to ticketing system. Is the server running on localhost:5000?"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def search_tickets_by_priority(priority: str) -> Dict[str, Any]:
    """Find tickets by their priority level.
    
    Args:
        priority: Priority to filter by (low, medium, high)
    
    Returns:
        Dictionary containing filtered tickets
    """
    try:
        # Get all tickets and filter by priority
        response = requests.get(f"{API_BASE_URL}/tickets")
        
        if response.status_code == 200:
            all_tickets = response.json()
            filtered_tickets = [t for t in all_tickets if t.get('priority', '').lower() == priority.lower()]
            
            return {
                "tickets": filtered_tickets,
                "count": len(filtered_tickets),
                "priority": priority,
                "summary": f"Found {len(filtered_tickets)} tickets with priority '{priority}'"
            }
        else:
            return {"error": handle_api_error(response)}
    
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to ticketing system. Is the server running on localhost:5000?"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}



@mcp.tool()
async def get_troubleshooting_guide(issue_description: str, ctx: Context = None) -> Dict[str, Any]:
    """Get the most relevant troubleshooting guide for a BeanBotics issue using AI selection.
    
    Uses MCP sampling to intelligently select the best troubleshooting guide and returns
    the complete markdown document with detailed troubleshooting steps.
    
    Args:
        issue_description: Description of the issue, symptoms, or error message
        ctx: MCP context for sampling
    
    Returns:
        Dictionary containing:
        - full_markdown_content: Complete troubleshooting guide in markdown format
        - guide_name: Name of the selected guide
        - selection_reason: Why this guide was chosen
    """
    # Available guides
    available_guides = [
        "robotic_arm - For robotic arm issues, error codes E003, servo problems, movement failures",
        "grinder_motor - For grinder motor overcurrent, grinding issues, burr problems", 
        "facial_recognition - For customer recognition failures, camera issues, identification problems",
        "boiler_temperature - For water temperature issues, heating problems, thermal control",
        "milk_frother - For milk frothing issues, steam wand problems, foam quality",
        "bean_hopper - For bean hopper sensor issues, level detection, insufficient beans errors"
    ]
    
    # Create sampling prompt
    prompt = f"""Issue: {issue_description}

Available troubleshooting guides:
{chr(10).join(['- ' + guide for guide in available_guides])}

Select the most relevant guide by responding with ONLY the guide name (e.g., "robotic_arm"):"""
    
    # Use MCP sampling to get AI selection
    response = await ctx.sample(messages=prompt)
    
    # Extract guide name from response
    selected_guide = response.text.strip().lower()
    
    # Validate selection
    valid_guides = ["robotic_arm", "grinder_motor", "facial_recognition", 
                   "boiler_temperature", "milk_frother", "bean_hopper"]
    
    if selected_guide not in valid_guides:
        selected_guide = "robotic_arm"  # Default if invalid response
    
    # Load the selected guide
    guide_content = load_troubleshooting_guide(selected_guide)
    
    return {
        "guide_name": selected_guide,
        "full_markdown_content": guide_content,
        "content": guide_content,  # Backward compatibility
        "selection_reason": f"AI-selected {selected_guide.replace('_', ' ')} troubleshooting guide based on issue: {issue_description}"
    }



if __name__ == "__main__":
    mcp.run(transport="http")