"""
tools.py
--------
Defines the tools (functions) the agent can call, and the logic
to execute them against the SQLite database.
"""

import sqlite3
import pandas as pd


# Tool schema - tells Claude what tools are available and how to call them
TOOLS = [
    {
        "name": "run_sql_query",
        "description": (
            "Run a read-only SQL query against the e-commerce SQLite database "
            "and return the results as rows. Use this for any question that "
            "requires looking up, aggregating, or filtering data."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A valid SQLite SELECT query.",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_table_schema",
        "description": (
            "Get the column names and types for a given table. "
            "Use this if you're unsure about exact column names before writing a query."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "Name of the table: orders, products, or customers.",
                }
            },
            "required": ["table_name"],
        },
    },
]


def execute_tool(tool_name: str, tool_input: dict, conn: sqlite3.Connection):
    """Routes a tool call to the right function and returns the result."""

    if tool_name == "run_sql_query":
        return _run_sql_query(tool_input["query"], conn)

    elif tool_name == "get_table_schema":
        return _get_table_schema(tool_input["table_name"], conn)

    return f"Unknown tool: {tool_name}"


def _run_sql_query(query: str, conn: sqlite3.Connection):
    """Executes a SQL query safely (read-only check) and returns results."""

    # Basic safety check - only allow SELECT statements
    normalized = query.strip().lower()
    if not normalized.startswith("select"):
        return "Error: Only SELECT queries are allowed."

    try:
        df = pd.read_sql_query(query, conn)
        if df.empty:
            return "Query executed successfully but returned no rows."

        # Limit output size for readability
        df = df.head(20)
        return df.to_string(index=False)

    except Exception as e:
        return f"SQL Error: {e}"


def _get_table_schema(table_name: str, conn: sqlite3.Connection):
    """Returns column info for a given table."""

    try:
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        if not columns:
            return f"Table '{table_name}' not found."

        result = f"Schema for '{table_name}':\n"
        for col in columns:
            result += f"  - {col[1]} ({col[2]})\n"
        return result

    except Exception as e:
        return f"Error: {e}"
