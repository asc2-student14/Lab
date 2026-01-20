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




if __name__ == "__main__":
    mcp.run(transport="http")