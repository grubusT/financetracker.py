import os
import sqlite3
from datetime import datetime

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


def display_menu():
    print("\nExpense Tracker")
    print("1. Add Expense")
    print("2. View All Expenses")
    print("3. View Expenses by Category")
    print("4. View Total Expenses")
    print("5. Remove Expense")
    print("6. Exit")
    return input("Select an option: ")


def main():
    tracker = ExpenseTracker()
    
    while True:
        choice = display_menu()
        
        if choice == "1":
            amount = input("Enter amount: ")
            print("Categories:", ", ".join(tracker.categories))
            category = input("Enter category: ")
            description = input("Enter description (optional): ")
            
            try:
                float(amount)
                if tracker.add_expense(amount, category, description):
                    print("Expense added successfully!")
                else:
                    print(f"Invalid category. Please choose from: {', '.join(tracker.categories)}")
            except ValueError:
                print("Invalid amount. Please enter a number.")
        
        elif choice == "2":
            expenses = tracker.get_expenses()
            if not expenses:
                print("No expenses recorded.")
            else:
                print("\nAll Expenses:")
                for expense in expenses:
                    print(f"ID: {expense['id']}, Amount: ${expense['amount']:.2f}, Category: {expense['category']}, "
                          f"Description: {expense['description']}, Date: {expense['date']}")
        
        elif choice == "3":
            print("Categories:", ", ".join(tracker.categories))
            category = input("Enter category to view: ")
            expenses = tracker.get_expenses(category)
            
            if not expenses:
                print(f"No expenses recorded for {category}.")
            else:
                print(f"\nExpenses for {category}:")
                for expense in expenses:
                    print(f"ID: {expense['id']}, Amount: ${expense['amount']:.2f}, "
                          f"Description: {expense['description']}, Date: {expense['date']}")
        
        elif choice == "4":
            total = tracker.get_total()
            print(f"\nTotal expenses: ${total:.2f}")
            
            print("\nExpenses by category:")
            for category in tracker.categories:
                cat_total = tracker.get_total(category)
                if cat_total > 0:
                    print(f"{category}: ${cat_total:.2f}")
        
        elif choice == "5":
            expenses = tracker.get_expenses()
            if not expenses:
                print("No expenses to remove.")
            else:
                print("\nCurrent Expenses:")
                for expense in expenses:
                    print(f"ID: {expense['id']}, Amount: ${expense['amount']:.2f}, Category: {expense['category']}")
                
                try:
                    expense_id = int(input("Enter the ID of the expense to remove: "))
                    if tracker.remove_expense(expense_id):
                        print("Expense removed successfully!")
                    else:
                        print("Expense ID not found.")
                except ValueError:
                    print("Invalid ID. Please enter a number.")
        
        elif choice == "6":
            print("Thank you for using Expense Tracker!")
            break
        
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main() 