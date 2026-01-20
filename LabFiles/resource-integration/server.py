#!/usr/bin/env python3
"""
Starter code for Lab: Resource Integration
Students will add MCP resource decorators to expose database functions as resources.
"""

import sqlite3
import logging
from datetime import datetime
from fastmcp import FastMCP

# Reduce logging verbosity for cleaner output
logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("mcp.server").setLevel(logging.ERROR)
logging.getLogger().setLevel(logging.WARNING)

# Initialize FastMCP server
mcp = FastMCP("InventoryServer")
DB_FILE = "inventory.db"


# ===== HELPER FUNCTIONS (shared by resources and tools) =====

def _get_inventory_summary() -> dict:
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


def _get_category_summary(cat: str) -> str:
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
    return f"Category: {cat}\nItems: {result[0]}\nAverage Price: ${result[1]:.2f}\nTotal Value: ${result[2]:.2f}"


def _get_item_in_category(cat: str, item_id: int) -> dict:
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


def _get_item_summary(item_id: int) -> dict:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, quantity, price, category, description
        FROM items 
        WHERE id = ?
    """, (item_id,))
    item = cursor.fetchone()
    conn.close()
    if not item:
        return {"error": f"Item {item_id} not found"}
    return {
        "id": item_id,
        "name": item[0],
        "quantity": item[1],
        "price": f"${item[2]:.2f}",
        "category": item[3],
        "description": item[4]
    }


def _get_categories() -> dict:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, COUNT(*) as item_count 
        FROM items 
        GROUP BY category 
        ORDER BY category
    """)
    categories = cursor.fetchall()
    conn.close()
    return {
        "available_categories": [
            {"name": cat[0], "item_count": cat[1]} for cat in categories
        ],
        "usage_hint": "Use these category names with inventory://category/{cat}"
    }


def _get_all_items() -> dict:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, category, price 
        FROM items 
        ORDER BY category, name
    """)
    items = cursor.fetchall()
    conn.close()
    return {
        "items": [
            {"id": item[0], "name": item[1], "category": item[2], "price": f"${item[3]:.2f}"}
            for item in items
        ],
        "usage_hint": "Use item IDs with inventory://category/{cat}/item/{item_id} or inventory://item_summary/{item_id}"
    }


# ===== RESOURCES =====

@mcp.resource("inventory://summary")
async def get_inventory_summary() -> dict:
    """Provides overall inventory statistics"""
    return _get_inventory_summary()


@mcp.resource("inventory://category/{cat}")
async def get_category_summary(cat: str) -> str:
    """Dynamic stats for any category"""
    return _get_category_summary(cat)


@mcp.resource("inventory://category/{cat}/item/{item_id}")
async def get_item_in_category(cat: str, item_id: int) -> dict:
    """Get detailed information about a specific item in a category"""
    return _get_item_in_category(cat, item_id)


@mcp.resource("inventory://item_summary/{item_id}")
async def get_item_summary(item_id: int) -> dict:
    """Comprehensive item summary combining item details and category stats"""
    return _get_item_summary(item_id)


@mcp.resource("inventory://categories")
async def get_categories() -> dict:
    """Lists all available categories in the inventory system"""
    return _get_categories()


@mcp.resource("inventory://items")
async def get_all_items() -> dict:
    """Lists all items with their IDs for easy reference"""
    return _get_all_items()


# ===== TOOLS (for agent interaction) =====

@mcp.tool()
async def list_categories() -> dict:
    """List all available inventory categories"""
    return _get_categories()


@mcp.tool()
async def list_items() -> dict:
    """List all items in the inventory"""
    return _get_all_items()


@mcp.tool()
async def get_summary() -> dict:
    """Get overall inventory statistics"""
    return _get_inventory_summary()


@mcp.tool()
async def get_category(category: str) -> str:
    """Get statistics for a specific category"""
    return _get_category_summary(category)


@mcp.tool()
async def get_item(item_id: int) -> dict:
    """Get details for a specific item by ID"""
    return _get_item_summary(item_id)


if __name__ == "__main__":
    mcp.run()
