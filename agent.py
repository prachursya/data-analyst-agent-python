"""
Data Analyst Agent
-------------------
An agentic AI system that:
1. Takes a natural language business question
2. Decides which tool to use (SQL query, summary stats, or chart)
3. Executes the tool against a local SQLite database
4. Returns results + AI-generated insights

Author: Prachursya
"""

import os
import sqlite3
import json
from anthropic import Anthropic
from dotenv import load_dotenv

from tools import TOOLS, execute_tool
from database import setup_database

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-20250514"

SYSTEM_PROMPT = """You are an autonomous Data Analyst Agent for an e-commerce business.

You have access to a SQLite database with these tables:
- orders(order_id, customer_id, product_id, category, quantity, price, order_date, status, city)
- products(product_id, name, category, cost_price, sell_price, stock)
- customers(customer_id, name, city, segment, signup_date)

When the user asks a business question:
1. Decide if you need to query the database using the run_sql_query tool
2. Write correct, efficient SQLite SQL
3. After receiving results, explain the findings in plain business language
4. Always end with 1-2 suggested follow-up questions

Be concise, accurate, and business-focused."""


def run_agent(user_question: str, conn: sqlite3.Connection, history: list) -> str:
    """
    Core agent loop:
    - Sends user question + conversation history to Claude
    - If Claude requests a tool (SQL query), executes it
    - Sends tool results back to Claude
    - Returns final natural-language answer
    """
    history.append({"role": "user", "content": user_question})

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=history,
        )

        # Check if the model wants to use a tool
        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]

        if not tool_use_blocks:
            # Final answer - no more tools needed
            final_text = "".join(
                b.text for b in response.content if b.type == "text"
            )
            history.append({"role": "assistant", "content": response.content})
            return final_text

        # Model wants to call a tool - add assistant's tool request to history
        history.append({"role": "assistant", "content": response.content})

        # Execute each requested tool and collect results
        tool_results = []
        for block in tool_use_blocks:
            print(f"\n🔧 Agent is using tool: {block.name}")
            print(f"   Input: {block.input}")

            result = execute_tool(block.name, block.input, conn)

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": str(result),
            })

        # Send tool results back to the model
        history.append({"role": "user", "content": tool_results})


def main():
    print("=" * 60)
    print("  📊 Data Analyst Agent (Agentic AI)")
    print("=" * 60)
    print("Setting up sample database...")

    conn = setup_database()
    print("Database ready ✅\n")
    print("Ask a business question (or type 'exit' to quit)")
    print("Examples:")
    print("  - Which product category generates the most revenue?")
    print("  - What's the average order value by city?")
    print("  - Show me customers who haven't ordered in 90 days")
    print("-" * 60)

    history = []

    while True:
        question = input("\n🧑 You: ").strip()
        if question.lower() in ("exit", "quit", "q"):
            print("Goodbye! 👋")
            break
        if not question:
            continue

        try:
            answer = run_agent(question, conn, history)
            print(f"\n🤖 Agent: {answer}")
        except Exception as e:
            print(f"\n⚠️ Error: {e}")

    conn.close()


if __name__ == "__main__":
    main()
