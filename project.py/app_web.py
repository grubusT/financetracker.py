from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Add template filters
@app.template_filter('formatdate')
def format_date(value, format='%Y-%m-%d'):
    if isinstance(value, str):
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    else:
        dt = value
    return dt.strftime(format)

@app.context_processor
def inject_now():
    return {'now': datetime}

class ExpenseTracker:
    def __init__(self):
        self.categories = ["Food", "Transportation", "Housing", "Entertainment", "Utilities", "Other"]
        self.db_file = "expenses.db"
        self.init_db()
    
    def get_db_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Create expenses table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
        ''')
        
        # Create categories table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        ''')
        
        # Insert default categories if they don't exist
        for category in self.categories:
            cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
        
        conn.commit()
        conn.close()
    
    def add_expense(self, amount, category, description=""):
        if category not in self.categories:
            return False
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
            (float(amount), category, description, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        conn.close()
        return True
    
    def remove_expense(self, expense_id):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    
    def get_expenses(self, category=None):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        if category and category != "All":
            cursor.execute("SELECT * FROM expenses WHERE category = ?", (category,))
        else:
            cursor.execute("SELECT * FROM expenses")
        
        expenses = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return expenses
    
    def get_total(self, category=None):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        if category and category != "All":
            cursor.execute("SELECT SUM(amount) as total FROM expenses WHERE category = ?", (category,))
        else:
            cursor.execute("SELECT SUM(amount) as total FROM expenses")
        
        result = cursor.fetchone()
        conn.close()
        
        # Return 0 if no expenses found
        return result['total'] or 0
    
    def get_category_totals(self):
        totals = {}
        for category in self.categories:
            totals[category] = self.get_total(category)
        return totals
    
    def get_monthly_totals(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # SQLite date functions to extract year and month
        cursor.execute('''
        SELECT 
            strftime('%Y-%m', date) as month,
            SUM(amount) as total
        FROM expenses
        GROUP BY month
        ORDER BY month
        ''')
        
        monthly_expenses = {row['month']: row['total'] for row in cursor.fetchall()}
        conn.close()
        
        return monthly_expenses


# Create expense tracker instance
tracker = ExpenseTracker()

@app.route('/')
def index():
    return render_template('index.html', 
                          categories=tracker.categories,
                          total=tracker.get_total(),
                          category_totals=tracker.get_category_totals())

@app.route('/expenses')
def expenses():
    category = request.args.get('category', default=None)
    expenses = tracker.get_expenses(category)
    return render_template('expenses.html', 
                          expenses=expenses, 
                          categories=tracker.categories,
                          selected_category=category)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    amount = request.form.get('amount')
    category = request.form.get('category')
    description = request.form.get('description', '')
    
    try:
        float(amount)
        if tracker.add_expense(amount, category, description):
            # Determine where to redirect based on the referer
            referer = request.headers.get('Referer', '')
            if '/expenses' in referer:
                return redirect(url_for('expenses', success=1))
            else:
                return redirect(url_for('index', success=1))
        else:
            return "Invalid category", 400
    except ValueError:
        return "Invalid amount", 400

@app.route('/remove_expense/<int:expense_id>', methods=['POST'])
def remove_expense(expense_id):
    if tracker.remove_expense(expense_id):
        return redirect(url_for('expenses', removed=1))
    else:
        return "Expense not found", 404

@app.route('/analytics')
def analytics():
    return render_template('analytics.html',
                          categories=tracker.categories,
                          total=tracker.get_total(),
                          category_totals=tracker.get_category_totals(),
                          monthly_totals=tracker.get_monthly_totals())

@app.route('/api/expenses')
def api_expenses():
    category = request.args.get('category', default=None)
    return jsonify(tracker.get_expenses(category))

@app.route('/api/category_totals')
def api_category_totals():
    return jsonify(tracker.get_category_totals())

@app.route('/api/monthly_totals')
def api_monthly_totals():
    return jsonify(tracker.get_monthly_totals())

if __name__ == '__main__':
    app.run(debug=True) 