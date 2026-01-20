#!/usr/bin/env python3
"""BeanBotics Seasonal Menu Creator"""
from typing import List, Dict
from dataclasses import dataclass
import json
from fastmcp import FastMCP
from fastmcp.server.context import Context

# Initialize the FastMCP server with sampling fallback
mcp = FastMCP("BeanBoticsSeasonalMenu")

@dataclass
class DrinkConcept:
    name: str
    description: str
    base_type: str
    theme: str
    
    @classmethod
    def json_schema(cls) -> str:
        return """{
  "drinks": [
    {"name": "drink name", "description": "brief description", "base_type": "latte|cappuccino|cold brew|frappuccino|tea latte|chai"}
  ]
}"""

@dataclass
class DrinkRecipe:
    name: str
    description: str
    ingredients: List[str]
    instructions: List[str]
    serving_size: str
    prep_time: str
    
    @classmethod
    def json_schema(cls) -> str:
        return """{
  "ingredients": ["ingredient with measurement"],
  "instructions": ["step by step"],
  "serving_size": "size",
  "prep_time": "time"
}"""



if __name__ == "__main__":
    mcp.run()
