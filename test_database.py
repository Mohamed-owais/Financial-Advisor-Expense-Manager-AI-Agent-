"""
Test Database Module - Verify SQLite expense tracking functionality
"""

import os
import sys
from datetime import datetime

# Add project directory to path
sys.path.insert(0, os.path.dirname(__file__))

from expense_tracker import ExpenseTracker

if __name__ == "__main__":
    print("=" * 60)
    print("TEST 3.2: DATABASE MODULE TEST")
    print("=" * 60)
    
    # Initialize database
    tracker = ExpenseTracker()
    print("\n✅ Database initialized successfully")
    
    # Add a sample expense
    print("\n📝 Adding sample expense...")
    sample_expense = {
        "amount": 250.50,
        "currency": "INR",
        "vendor": "McDonald's",
        "category": "Food & Dining",
        "items": ["Burger", "Fries", "Coke"],
        "date": datetime.now().strftime("%Y-%m-%d"),
        "payment_method": "card",
        "notes": "Lunch with team"
    }
    
    result = tracker.add_expense(sample_expense)
    if result:
        print(f"✅ Expense added successfully (ID: {result})")
    else:
        print("❌ Failed to add expense")
    
    # Retrieve all expenses
    print("\n📊 Retrieving all expenses...")
    expenses = tracker.get_all_expenses()
    print(f"✅ Found {len(expenses)} expense(s)")
    
    if not expenses.empty:
        print("\nExpense Details:")
        for idx, exp in expenses.iterrows():
            print(f"  ID: {exp['id']}")
            print(f"  Amount: ₹{exp['amount']} {exp['currency']}")
            print(f"  Vendor: {exp['vendor']}")
            print(f"  Category: {exp['category']}")
            print(f"  Date: {exp['date']}")
            print(f"  Items: {exp['items']}")
            print()
    
    # Get category summary
    print("📈 Category Summary:")
    summary = tracker.get_monthly_summary()
    if summary:
        for key, value in summary.items():
            print(f"  {key}: ₹{value}")
    else:
        print("  No data available")
    
    # Check if database file exists
    print("\n" + "=" * 60)
    if os.path.exists("expenses.db"):
        size = os.path.getsize("expenses.db")
        print(f"✅ Database file created: expenses.db ({size} bytes)")
    else:
        print("❌ Database file not found")
    
    print("=" * 60)
    print("TEST 3.2 COMPLETE")
    print("=" * 60)
    print("\nNext: Run test_groq.py")