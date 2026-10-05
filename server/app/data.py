"""
Mock data for the Factory Inventory Management System
This module loads sample data from JSON files for inventory items, orders, demand forecasts, and backlog items.
Data covers all months of 2025 and includes warehouse, category, and date fields for filtering.

Everything is loaded once at import and shared by all routers: treat these objects as read-only
(except purchase_orders, which is the store new purchase orders are appended to).
"""

import json
import os

# server/ is the parent of this package; JSON files live in server/data/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def load_json_file(filename):
    """Load data from a JSON file in the data directory"""
    filepath = os.path.join(DATA_DIR, filename)
    # Explicit encoding: the locale default on Windows (cp1252) garbles characters like '±'
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# Load all datasets from JSON files
inventory_items = load_json_file('inventory.json')
orders = load_json_file('orders.json')
demand_forecasts = load_json_file('demand_forecasts.json')
backlog_items = load_json_file('backlog_items.json')

# Load spending data
spending_data = load_json_file('spending.json')
spending_summary = spending_data['spending_summary']
monthly_spending = spending_data['monthly_spending']
category_spending = spending_data['category_spending']

# Load transactions
recent_transactions = load_json_file('transactions.json')

# Load purchase orders
purchase_orders = load_json_file('purchase_orders.json')

# All data is now loaded from JSON files in the data/ directory
# This allows for easier maintenance and updates of the sample data
