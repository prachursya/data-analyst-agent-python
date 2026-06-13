"""
Offline Data Analyst Agent
----------------------------
A rule-based "agentic" data analyst that works with a sample
SQLite database. No API key, no internet, no cost.

The agent:
1. Parses your natural language question
2. Picks the right pre-built analysis (its "tool")
3. Runs SQL against the sample database
4. Returns results + auto-generated insights

Author: Prachursya
"""

import sqlite3
import re
from database import setup_database


# ---------------------------------------------------------
# "Tools" the agent can choose from
# ---------------------------------------------------------

def revenue_by_category(conn):
    query = """
        SELECT category, ROUND(SUM(price * quantity), 2) AS revenue
        FROM orders
        WHERE status != 'Cancelled'
        GROUP BY category
        ORDER BY revenue DESC
    """
    return query, conn.execute(query).fetchall(), ["category", "revenue"]


def revenue_by_city(conn):
    query = """
        SELECT city, ROUND(SUM(price * quantity), 2) AS revenue
        FROM orders
        WHERE status != 'Cancelled'
        GROUP BY city
        ORDER BY revenue DESC
    """
    return query, conn.execute(query).fetchall(), ["city", "revenue"]


def top_products(conn):
    query = """
        SELECT p.name, p.category, SUM(o.quantity) AS units_sold
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        WHERE o.status != 'Cancelled'
        GROUP BY p.name, p.category
        ORDER BY units_sold DESC
        LIMIT 5
    """
    return query, conn.execute(query).fetchall(), ["product", "category", "units_sold"]


def order_status_breakdown(conn):
    query = """
        SELECT status, COUNT(*) AS order_count
        FROM orders
        GROUP BY status
        ORDER BY order_count DESC
    """
    return query, conn.execute(query).fetchall(), ["status", "order_count"]


def avg_order_value_by_segment(conn):
    query = """
        SELECT c.segment, ROUND(AVG(o.price * o.quantity), 2) AS avg_order_value
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.status != 'Cancelled'
        GROUP BY c.segment
        ORDER BY avg_order_value DESC
    """
    return query, conn.execute(query).fetchall(), ["segment", "avg_order_value"]


def low_stock_products(conn):
    query = """
        SELECT name, category, stock
        FROM products
        WHERE stock < 50
        ORDER BY stock ASC
    """
    return query, conn.execute(query).fetchall(), ["product", "category", "stock"]


def margin_by_category(conn):
    query = """
        SELECT category,
               ROUND(AVG(sell_price - cost_price), 2) AS avg_margin
        FROM products
        GROUP BY category
        ORDER BY avg_margin DESC
    """
    return query, conn.execute(query).fetchall(), ["category", "avg_margin"]


# ---------------------------------------------------------
# Agent "brain": maps question keywords -> tool
# ---------------------------------------------------------

TOOL_MAP = [
    (["revenue", "category"], revenue_by_category,
     "Revenue by product category"),
    (["revenue", "city"], revenue_by_city,
     "Revenue by city"),
    (["top", "product"], top_products,
     "Top-selling products by units"),
    (["status", "order status", "cancelled", "delivered"], order_status_breakdown,
     "Order status breakdown"),
    (["average order", "aov", "order value"], avg_order_value_by_segment,
     "Average order value by customer segment"),
    (["low stock", "stock", "inventory"], low_stock_products,
     "Products running low on stock"),
    (["margin", "profit"], margin_by_category,
     "Average profit margin by category"),
]


def pick_tool(question: str):
    """Very simple keyword-based 'reasoning' to pick the right tool."""
    q = question.lower()

    for keywords, func, description in TOOL_MAP:
        if any(k in q for k in keywords):
            return func, description

    return None, None


# ---------------------------------------------------------
# Insight generation (simple rule-based "explanation")
# ---------------------------------------------------------

def generate_insight(rows, columns):
    if not rows:
        return "No data found for this query."

    insights = []
    top_row = rows[0]

    # Generic insight: highlight the top row
    label_col = columns[0]
    value_col = columns[-1]
    insights.append(
        f"• Top result: **{top_row[0]}** leads with {value_col} = {top_row[-1]}"
    )

    if len(rows) > 1:
        bottom_row = rows[-1]
        insights.append(
            f"• Lowest: **{bottom_row[0]}** with {value_col} = {bottom_row[-1]}"
        )

    if len(rows) > 2:
        insights.append(f"• {len(rows)} categories/segments analyzed in total.")

    return "\n".join(insights)


# ---------------------------------------------------------
# Pretty print results as a table
# ---------------------------------------------------------

def print_table(columns, rows):
    if not rows:
        print("No results.")
        return

    widths = [max(len(str(col)), max(len(str(r[i])) for r in rows)) + 2
              for i, col in enumerate(columns)]

    header = "".join(f"{col:<{widths[i]}}" for i, col in enumerate(columns))
    print(header)
    print("-" * len(header))

    for row in rows:
        print("".join(f"{str(val):<{widths[i]}}" for i, val in enumerate(row)))


# ---------------------------------------------------------
# Main loop
# ---------------------------------------------------------

def main():
    print("=" * 60)
    print("  📊 Offline Data Analyst Agent (Free - No API Key)")
    print("=" * 60)
    print("Setting up sample database (50 customers, 30 products, 500 orders)...")

    conn = setup_database()
    print("Database ready ✅\n")

    print("This agent picks the right analysis based on your question.")
    print("Try asking about:")
    print("  - revenue by category")
    print("  - revenue by city")
    print("  - top products")
    print("  - order status breakdown")
    print("  - average order value")
    print("  - low stock products")
    print("  - profit margin by category")
    print("-" * 60)

    while True:
        question = input("\n🧑 You: ").strip()

        if question.lower() in ("exit", "quit", "q"):
            print("Goodbye! 👋")
            break

        if not question:
            continue

        tool, description = pick_tool(question)

        if tool is None:
            print("\n🤖 Agent: I couldn't match that to one of my analyses.")
            print("   Try rephrasing using words like: revenue, category, city,")
            print("   top products, order status, average order value, stock, or margin.")
            continue

        print(f"\n🔧 Agent selected analysis: {description}")

        query, rows, columns = tool(conn)

        print(f"\n📝 SQL used:\n{query.strip()}")
        print(f"\n📊 Results:")
        print_table(columns, rows)

        print(f"\n💡 Insights:")
        print(generate_insight(rows, columns))

    conn.close()


if __name__ == "__main__":
    main()
