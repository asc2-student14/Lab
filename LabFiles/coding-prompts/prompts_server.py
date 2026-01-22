from fastmcp import FastMCP
import os

# Initialize the FastMCP server
mcp = FastMCP("CodingPromptsServer")

# Directory containing prompt template files (one level up from solutions/)
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")

@mcp.prompt()
async def support_ticket_triage(ticket_id: str, issue_description: str, provided_info: str) -> str:
    """Triage a support ticket and ensure complete information gathering."""
    with open(os.path.join(PROMPTS_DIR, 'support_ticket_triage.prompt.md')) as f:
        template = f.read()
        return template.replace("{ticket_id}", ticket_id).replace("{issue_description}", issue_description).replace("{provided_info}", provided_info)

@mcp.prompt()
async def escalation_decision(
    ticket_id: str,
    issue_summary: str,
    customer_tier: str = "standard",
    previous_tickets: str = "none",
    troubleshooting_attempted: str = "none"
) -> str:
    """Make consistent escalation decisions based on clear criteria."""
    with open(os.path.join(PROMPTS_DIR, 'escalation_decision.prompt.md')) as f:
        template = f.read()
        template = template.replace("{ticket_id}", ticket_id)
        template = template.replace("{issue_summary}", issue_summary)
        template = template.replace("{customer_tier}", customer_tier)
        template = template.replace("{previous_tickets}", previous_tickets)
        template = template.replace("{troubleshooting_attempted}", troubleshooting_attempted)
        return template

@mcp.prompt()
async def document_function(function_name: str = "") -> str:
    """Generate documentation standards for Python functions."""
    with open(os.path.join(PROMPTS_DIR, 'document_function.prompt.md')) as f:
        template = f.read()
        if function_name:
            return template.replace("{function_name}", function_name)
        return template.replace("Focus on {function_name} in the provided code.", "Focus on the selected code.")

@mcp.prompt()
async def code_review_checklist(focus_area: str = "general") -> str:
    """Perform systematic code review with specific focus areas."""
    # Map focus areas to descriptions
    focus_descriptions = {
        "database": "Database operations, connection handling, and SQL practices",
        "error_handling": "Exception handling, error messages, and recovery",
        "security": "Input validation, SQL injection, authentication",
        "performance": "Efficiency, caching, and resource usage",
        "general": "Overall code quality, style, and maintainability"
    }
    
    focus_description = focus_descriptions.get(focus_area, focus_descriptions["general"])
    
    with open(os.path.join(PROMPTS_DIR, 'code_review_checklist.prompt.md')) as f:
        template = f.read()
        return template.replace("{focus_description}", focus_description)

@mcp.prompt()
async def debug_assistant(
    problem_description: str,
    error_symptoms: str = "",
    suspected_area: str = ""
) -> str:
    """Provide systematic debugging guidance for code issues."""
    with open(os.path.join(PROMPTS_DIR, 'debug_assistant.prompt.md')) as f:
        template = f.read()
        
        # Replace template variables, using defaults for optional parameters
        template = template.replace("{problem_description}", problem_description)
        template = template.replace("{error_symptoms}", error_symptoms or "Not specified")
        template = template.replace("{suspected_area}", suspected_area or "Not specified")
        
        return template

if __name__ == "__main__":
    mcp.run(transport="http")