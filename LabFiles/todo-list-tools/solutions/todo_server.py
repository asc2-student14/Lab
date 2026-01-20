#!/usr/bin/env python3
"""Todo List MCP Server - Complete Solution

This server provides tools for AI assistants to manage their own todo lists
when working on complex, multi-step projects.
"""
from fastmcp import FastMCP
from dataclasses import dataclass
from typing import List

# Initialize the FastMCP server
mcp = FastMCP("TodoList")

@dataclass
class Todo:
    id: int
    todo: str
    completed: bool = False

class TodoList:
    def __init__(self):
        self.next_id = 1
        self.todos = {}
    
    def add(self, todo: str) -> Todo:
        new_todo = Todo(id=self.next_id, todo=todo)
        self.todos[self.next_id] = new_todo
        self.next_id += 1
        return new_todo

    def complete(self, todo_id: int) -> Todo:
        self.todos[todo_id].completed = True
        return self.todos[todo_id]


todo_list = TodoList()

# [SOLUTION]
@mcp.tool()
def add_todo(todo: str) -> Todo:
    """Add a new todo item."""
    return todo_list.add(todo)

@mcp.tool()
def list_todos() -> List[Todo]:
    """List all todo items."""
    return list(todo_list.todos.values())

@mcp.tool()
def complete_todo(todo_id: int) -> Todo:
    """Mark a todo item as completed."""
    return todo_list.complete(todo_id)

@mcp.tool()
def clear_list() -> None:
    """Clear all todo items."""
    todo_list.todos.clear()
    todo_list.next_id = 1
# [/SOLUTION]

if __name__ == "__main__":
    mcp.run(transport="http")
