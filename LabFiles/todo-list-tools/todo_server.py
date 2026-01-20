#!/usr/bin/env python3
"""Todo List MCP Server - Starter Code

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

# Create an instance of the TodoList
todo_list = TodoList()




if __name__ == "__main__":
    mcp.run(transport="http")
