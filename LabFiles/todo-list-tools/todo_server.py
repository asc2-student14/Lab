#!/usr/bin/env python3
"""Todo List MCP Server - Starter Code

This server provides tools for AI assistants to manage their own todo lists
when working on complex, multi-step projects.
"""
from fastmcp import FastMCP
from dataclasses import dataclass
from typing import Any, List
from pathlib import Path
import yaml

# Initialize the FastMCP server
mcp = FastMCP[Any]("TodoList")

# Path to recipes directory
RECIPES_DIR = Path(__file__).parent / "recipes"

@dataclass
class Todo:
    id: int
    todo: str
    completed: bool = False

class TodoList:
    def __init__(self):
        self.next_id = 1
        self.todos = {}
    
    def clear(self) -> None:
        self.todos.clear()
        self.next_id = 1
    
    def add(self, todo: str) -> Todo:
        new_todo = Todo(id=self.next_id, todo=todo)
        self.todos[self.next_id] = new_todo
        self.next_id += 1
        return new_todo

    def complete(self, todo_id: int) -> Todo:
        self.todos[todo_id].completed = True
        return self.todos[todo_id]

# Create an instance of the TodoList
todo_list = TodoList()

@mcp.tool()
def add_todo(todo: str) -> Todo:
    """Add a new todo item."""
    return todo_list.add(todo)

@mcp.tool()
def list_todos() -> List[Todo]:
    """List all todo items."""
    return list[Todo](todo_list.todos.values())

@mcp.tool()
def complete_todo(todo_id: int) -> Todo:
    """Mark a todo item as completed."""
    return todo_list.complete(todo_id)

@mcp.tool()
def clear_list() -> None:
    """Clear all todo items."""
    return todo_list.clear()


@mcp.tool()
def load_todos_from_yaml(filename: str) -> List[Todo]:
    """Load todos from a YAML file in the recipes directory.
    
    Args:
        filename: Name of the YAML file (e.g., 'cappuccino.yml', 'espresso.yml')
    
    Returns:
        List of Todo items that were added
    """
    file_path = RECIPES_DIR / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"Recipe file not found: {filename}")
    
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    
    added_todos = []
    for todo_text in data.get('todos', []):
        new_todo = todo_list.add(todo_text)
        added_todos.append(new_todo)
    
    return added_todos


if __name__ == "__main__":
    mcp.run(transport="http")
