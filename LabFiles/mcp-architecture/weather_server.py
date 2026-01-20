#!/usr/bin/env python3
"""
Weather Information MCP Server

A demonstration MCP server that provides weather information through tools, resources, and prompts.
"""

from datetime import datetime
from fastmcp import FastMCP
from typing import List

# Initialize the MCP server
mcp = FastMCP("Weather Information Server")

# Simple weather data for demonstration
WEATHER_DATA = {
    "seattle": {"temp": 52, "condition": "Partly Cloudy", "humidity": 68},
    "portland": {"temp": 58, "condition": "Light Rain", "humidity": 78},
    "denver": {"temp": 72, "condition": "Sunny", "humidity": 35},
    "chicago": {"temp": 48, "condition": "Windy", "humidity": 62},
}

ALERTS = {
    "seattle": ["Wind Advisory: Gusts up to 35 mph expected"],
    "chicago": ["High Wind Warning: Damaging winds up to 60 mph"],
}

# ===== TOOLS =====

@mcp.tool()
async def get_current_weather(location: str) -> dict:
    """Get current weather conditions for a location."""
    location = location.lower()
    
    if location not in WEATHER_DATA:
        return {"error": f"Location '{location}' not found. Available: {list(WEATHER_DATA.keys())}"}
    
    data = WEATHER_DATA[location].copy()
    data["location"] = location.title()
    data["updated"] = datetime.now().isoformat()
    return data

@mcp.tool()  
async def get_forecast(location: str, days: int = 3) -> dict:
    """Get weather forecast for a location."""
    location = location.lower()
    
    if location not in WEATHER_DATA:
        return {"error": f"Location '{location}' not found"}
    
    if days < 1 or days > 7:
        return {"error": "Days must be between 1 and 7"}
    
    current_temp = WEATHER_DATA[location]["temp"]
    
    return {
        "location": location.title(),
        "days_requested": days,
        "forecast": {
            "tomorrow": {"high": current_temp + 3, "low": current_temp - 8, "condition": "Sunny"},
            "day_after": {"high": current_temp + 1, "low": current_temp - 6, "condition": "Cloudy"}
        },
        "generated_at": datetime.now().isoformat()
    }

@mcp.tool()
async def get_weather_alerts(location: str) -> dict:
    """Get weather alerts for a location."""
    location = location.lower()
    
    if location not in WEATHER_DATA:
        return {"error": f"Location '{location}' not found"}
    
    alerts = ALERTS.get(location, [])
    return {
        "location": location.title(),
        "alert_count": len(alerts),
        "alerts": alerts
    }

# ===== RESOURCES =====

@mcp.resource("weather://locations")
async def list_locations() -> List[str]:
    """List all supported weather locations"""
    return list(WEATHER_DATA.keys())

@mcp.resource("weather://current/{location}")
async def current_weather_resource(location: str) -> dict:
    """Get current weather as a resource"""
    location = location.lower()
    
    if location not in WEATHER_DATA:
        return {"error": f"Location '{location}' not supported"}
    
    return WEATHER_DATA[location]

# ===== PROMPTS =====

@mcp.prompt()
async def weather_report(location: str = "Seattle", current_conditions: str = "") -> str:
    """Generate a weather report prompt template"""
    conditions_text = f"\n\nCurrent Conditions Data:\n{current_conditions}" if current_conditions else ""
    
    return f"""Create a weather report for {location}. Include:

1. Current conditions (temperature, sky, humidity)
2. Today's forecast and any weather advisories
3. Recommendations for outdoor activities
4. What to wear based on conditions

Use a friendly, informative tone suitable for the general public.{conditions_text}"""

if __name__ == "__main__":
    mcp.run(transport="http")