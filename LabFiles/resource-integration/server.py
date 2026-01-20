#!/usr/bin/env python3
"""
Starter code for Lab: Resource Integration
Students will add MCP resource decorators to expose database functions as resources.
"""

import asyncio
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any
from fastmcp import FastMCP, Context

# Reduce logging verbosity for cleaner output
logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("mcp.server").setLevel(logging.ERROR)
logging.getLogger().setLevel(logging.WARNING)

# Initialize FastMCP server
mcp = FastMCP("InventoryServer")
DB_FILE = "inventory.db"


@mcp.resource("inventory://summary")
async def get_inventory_summary() -> dict:
    """Provides overall inventory statistics"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM items")
    total_items = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT category) FROM items")
    total_categories = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(quantity * price) FROM items")
    total_value = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        "total_items": total_items,
        "total_categories": total_categories,
        "total_value": f"${total_value:.2f}",
        "timestamp": datetime.now().isoformat()
    }


@mcp.resource("inventory://category/{cat}")
async def get_category_summary(cat: str) -> str:
    """Dynamic stats for any category"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as item_count,
            AVG(price) as avg_price,
            SUM(quantity * price) as total_value
        FROM items 
        WHERE category = ?
    """, (cat,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result[0] == 0:
        return f"No items found in category '{cat}'"
    
    return f"Category: {cat}\n" \
           f"Items: {result[0]}\n" \
           f"Average Price: ${result[1]:.2f}\n" \
           f"Total Value: ${result[2]:.2f}"


@mcp.resource("inventory://category/{cat}/item/{item_id}")
async def get_item_in_category(cat: str, item_id: int) -> dict:
    """Get detailed information about a specific item in a category"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name, quantity, price, description, last_updated
        FROM items 
        WHERE category = ? AND id = ?
    """, (cat, item_id))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        raise ValueError(f"Item {item_id} not found in category '{cat}'")
    
    return {
        "id": item_id,
        "category": cat,
        "name": result[0],
        "quantity": result[1],
        "price": result[2],
        "description": result[3],
        "last_updated": result[4]
    }


@mcp.resource("inventory://item_summary/{item_id}")
async def get_item_summary(item_id: int) -> dict:
    """Comprehensive item summary combining item details and category stats"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Fetch item details
    cursor.execute("""
        SELECT name, quantity, price, category, description
        FROM items 
        WHERE id = ?
    """, (item_id,))
    
    item = cursor.fetchone()
    conn.close()
    
    if not item:
        raise ValueError(f"Item {item_id} not found")
    
    # TODO: Call get_category_summary() to get category statistics
    # category_stats = await get_category_summary(item[3])
    category_stats = "Not yet implemented"
    
    # TODO: Add ctx.request_id to the return dict (requires Context parameter)
    return {
        "item": {
            "id": item_id,
            "name": item[0],
            "quantity": item[1],
            "price": item[2],
            "category": item[3],
            "description": item[4]
        },
        "category_stats": category_stats,
        # "request_id": ctx.request_id  # Add this after adding Context parameter
    }

if __name__ == "__main__":
    mcp.run()