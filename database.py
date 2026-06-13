"""
database.py
-----------
Creates an in-memory SQLite database with realistic sample
e-commerce data: orders, products, and customers.
"""

import sqlite3
import random
from datetime import datetime, timedelta


def setup_database() -> sqlite3.Connection:
    """Creates and populates an in-memory SQLite database. Returns the connection."""

    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # ---------- Create tables ----------
    cursor.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT,
            city TEXT,
            segment TEXT,
            signup_date TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            cost_price REAL,
            sell_price REAL,
            stock INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            category TEXT,
            quantity INTEGER,
            price REAL,
            order_date TEXT,
            status TEXT,
            city TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)

    # ---------- Sample data ----------
    cities = ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai", "Pune", "Kolkata"]
    segments = ["Premium", "Regular", "New"]
    categories = ["Electronics", "Fashion", "Home & Kitchen", "Beauty", "Sports", "Books"]
    statuses = ["Delivered", "Shipped", "Cancelled", "Returned", "Processing"]

    # Customers
    customers = []
    for i in range(1, 51):
        signup = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 700))
        customers.append((
            i,
            f"Customer {i}",
            random.choice(cities),
            random.choice(segments),
            signup.strftime("%Y-%m-%d"),
        ))
    cursor.executemany(
        "INSERT INTO customers VALUES (?, ?, ?, ?, ?)", customers
    )

    # Products
    product_names = {
        "Electronics": ["Wireless Earbuds", "Smartwatch", "Bluetooth Speaker", "Power Bank", "USB Cable"],
        "Fashion": ["Cotton T-Shirt", "Denim Jeans", "Running Shoes", "Leather Wallet", "Sunglasses"],
        "Home & Kitchen": ["Non-stick Pan", "Coffee Maker", "LED Lamp", "Storage Box", "Cutlery Set"],
        "Beauty": ["Face Wash", "Moisturizer", "Lipstick Set", "Hair Dryer", "Perfume"],
        "Sports": ["Yoga Mat", "Dumbbell Set", "Cricket Bat", "Football", "Resistance Bands"],
        "Books": ["Fiction Novel", "Self-Help Book", "Cookbook", "Biography", "Comic Book"],
    }

    products = []
    pid = 1
    for category, names in product_names.items():
        for name in names:
            cost = round(random.uniform(100, 2000), 2)
            sell = round(cost * random.uniform(1.2, 1.8), 2)
            stock = random.randint(0, 500)
            products.append((pid, name, category, cost, sell, stock))
            pid += 1

    cursor.executemany(
        "INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)", products
    )

    # Orders
    orders = []
    for i in range(1, 501):
        customer = random.choice(customers)
        product = random.choice(products)
        order_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 500))
        quantity = random.randint(1, 5)

        orders.append((
            i,
            customer[0],
            product[0],
            product[2],          # category
            quantity,
            product[4],           # sell_price
            order_date.strftime("%Y-%m-%d"),
            random.choice(statuses),
            customer[2],          # city
        ))

    cursor.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", orders
    )

    conn.commit()
    return conn
