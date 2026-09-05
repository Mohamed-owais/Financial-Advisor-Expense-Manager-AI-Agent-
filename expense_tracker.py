DATABASE_PATH = 'expenses.db'
"""
Financial Advisor MVP - Expense Tracker
Manages SQLite database for storing and analyzing expenses
"""

import sqlite3
import json
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path
import config

class ExpenseTracker:
    def __init__(self, db_path=None):
        """
        Initialize expense tracker with SQLite database
        
        Args:
            db_path: Path to SQLite database file (default: expenses.db)
        """
        self.db_path = db_path or config.DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create expenses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'INR',
                    vendor TEXT NOT NULL,
                    category TEXT NOT NULL,
                    items TEXT,
                    date TEXT NOT NULL,
                    payment_method TEXT,
                    notes TEXT,
                    receipt_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create budget table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT UNIQUE NOT NULL,
                    monthly_limit REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create summary table for analytics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monthly_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    year INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    total_spent REAL DEFAULT 0,
                    transaction_count INTEGER DEFAULT 0,
                    UNIQUE(year, month, category)
                )
            ''')
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            return False
    
    def add_expense(self, expense_data):
        """
        Add a new expense to database
        
        Args:
            expense_data: dict with keys: amount, currency, vendor, category, 
                         items, date, payment_method, notes, receipt_text
        
        Returns:
            dict: Success/failure response with expense ID
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Parse items list to JSON string if needed
            items = expense_data.get('items', [])
            if isinstance(items, list):
                items = json.dumps(items)
            
            cursor.execute('''
                INSERT INTO expenses 
                (amount, currency, vendor, category, items, date, payment_method, notes, receipt_text)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                float(expense_data.get('amount', 0)),
                expense_data.get('currency', 'INR'),
                expense_data.get('vendor', 'Unknown'),
                expense_data.get('category', 'Other'),
                items,
                expense_data.get('date', datetime.now().strftime("%Y-%m-%d")),
                expense_data.get('payment_method', 'unknown'),
                expense_data.get('notes', ''),
                expense_data.get('receipt_text', '')
            ))
            
            expense_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "expense_id": expense_id,
                "message": f"Expense #{expense_id} added successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to add expense: {str(e)}"
            }
    
    def get_all_expenses(self):
        """Get all expenses from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query("SELECT * FROM expenses ORDER BY date DESC", conn)
            conn.close()
            
            # Convert items JSON strings back to lists
            if not df.empty:
                df['items'] = df['items'].apply(
                    lambda x: json.loads(x) if x and isinstance(x, str) else []
                )
            
            return df
        except Exception as e:
            print(f"❌ Error retrieving expenses: {e}")
            return pd.DataFrame()
    
    def get_expenses_by_category(self):
        """Get total expenses grouped by category"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT category, SUM(amount) as total, COUNT(*) as count
                FROM expenses
                GROUP BY category
                ORDER BY total DESC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            return {
                "categories": [r[0] for r in results],
                "totals": [float(r[1]) for r in results],
                "counts": [r[2] for r in results]
            }
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}
    
    def get_expenses_by_date_range(self, start_date, end_date):
        """Get expenses within a date range"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM expenses
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC
            ''', (start_date, end_date))
            
            df = pd.read_sql_query(
                f"SELECT * FROM expenses WHERE date BETWEEN '{start_date}' AND '{end_date}' ORDER BY date DESC",
                conn
            )
            conn.close()
            
            return df
        except Exception as e:
            print(f"❌ Error: {e}")
            return pd.DataFrame()
    
    def get_monthly_summary(self, year=None, month=None):
        """Get expense summary for a specific month"""
        try:
            if not year:
                year = datetime.now().year
            if not month:
                month = datetime.now().month
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT category, SUM(amount) as total, COUNT(*) as count
                FROM expenses
                WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
                GROUP BY category
                ORDER BY total DESC
            ''', (str(year).zfill(4), str(month).zfill(2)))
            
            results = cursor.fetchall()
            total_spent = sum(r[1] for r in results)
            
            conn.close()
            
            return {
                "year": year,
                "month": month,
                "total_spent": float(total_spent),
                "breakdown": [
                    {"category": r[0], "amount": float(r[1]), "count": r[2]}
                    for r in results
                ]
            }
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}
    
    def get_spending_trend(self, months=6):
        """Get spending trend for last N months"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(f'''
                SELECT 
                    strftime('%Y-%m', date) as month,
                    SUM(amount) as total,
                    COUNT(*) as count
                FROM expenses
                WHERE date >= date('now', '-{months} months')
                GROUP BY strftime('%Y-%m', date)
                ORDER BY month ASC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            return {
                "months": [r[0] for r in results],
                "totals": [float(r[1]) for r in results],
                "counts": [r[2] for r in results]
            }
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}
    
    def delete_expense(self, expense_id):
        """Delete an expense by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()
            conn.close()
            
            return {"success": True, "message": f"Expense #{expense_id} deleted"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def export_to_csv(self, output_path=None):
        """Export all expenses to CSV file"""
        try:
            if not output_path:
                output_path = f"expenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            df = self.get_all_expenses()
            if df.empty:
                return {"success": False, "error": "No expenses to export"}
            
            df.to_csv(output_path, index=False)
            return {
                "success": True,
                "message": f"Exported {len(df)} expenses to {output_path}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# Test the tracker
if __name__ == "__main__":
    tracker = ExpenseTracker()
    print("✅ Expense Tracker initialized")
    print(f"Database: {tracker.db_path}")
    
    # Test adding a sample expense
    sample = {
        "amount": 250,
        "currency": "INR",
        "vendor": "Madurai Café",
        "category": "Food & Dining",
        "items": ["Coffee", "Sandwich"],
        "date": datetime.now().strftime("%Y-%m-%d"),
        "payment_method": "card"
    }
    result = tracker.add_expense(sample)
    print(result)
