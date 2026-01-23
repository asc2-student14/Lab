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

# [SOLUTION]
@mcp.tool()
async def generate_themed_drinks(
    theme: str,
    count: int = 5,
    ctx: Context = None
) -> List[DrinkConcept]:
    """Generate themed seasonal drink concepts."""
    
    # Simple JSON prompt
    prompt = f"""Generate {count} {theme} themed drinks for a coffee shop. Return as JSON:

{DrinkConcept.json_schema()}"""

    response = await ctx.sample(messages=prompt)
    
    try:
        data = json.loads(response.text)
        return [
            DrinkConcept(
                name=drink["name"],
                description=drink["description"],
                base_type=drink["base_type"],
                theme=theme
            )
            for drink in data["drinks"]
        ]
    except (json.JSONDecodeError, KeyError):
        return []


@mcp.tool()
async def generate_drink_recipe(
    drink_name: str,
    description: str,
    base_type: str,
    dietary_restrictions: str = "none",
    ctx: Context = None
) -> DrinkRecipe:
    """Generate a complete recipe for a seasonal drink concept."""
    
    prompt = f"""Create a recipe for "{drink_name}" ({base_type}) with dietary restrictions: {dietary_restrictions}.
Return as JSON:

{DrinkRecipe.json_schema()}"""

    response = await ctx.sample(messages=prompt)
    
    try:
        data = json.loads(response.text)
        return DrinkRecipe(
            name=drink_name,
            description=description,
            ingredients=data.get("ingredients", []),
            instructions=data.get("instructions", []),
            serving_size=data.get("serving_size", "12 oz"),
            prep_time=data.get("prep_time", "3-5 minutes")
        )
    except (json.JSONDecodeError, KeyError):
        return DrinkRecipe(
            name=drink_name,
            description=description,
            ingredients=[],
            instructions=[],
            serving_size="12 oz",
            prep_time="3-5 minutes"
        )


@mcp.tool()
async def score_drink_concept(
    drink_name: str,
    recipe: str,
    ctx: Context = None
) -> int:
    """Score a drink concept from 1-5 based on overall appeal."""
    
    prompt = f"""Evaluate this drink concept and provide a score from 1-5 (1=poor, 5=excellent).
Consider creativity, market appeal, and complexity.

Drink: {drink_name}
Recipe: {recipe}

Respond with ONLY a single number from 1 to 5."""

    # Run the prompt
    response = await ctx.sample(messages=prompt)
   
    # Extract the numeric score from the response
    score = int(response.text.strip())
    
    # Ensure score is within valid range
    return max(1, min(5, score))
# [/SOLUTION]

if __name__ == "__main__":
    mcp.run()
