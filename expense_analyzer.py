import os
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import calendar

class ExpenseAnalyzer:
    def __init__(self, db_file="expenses.db"):
        self.db_file = db_file
        self.init_db()
    
    def get_db_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        if not os.path.exists(self.db_file):
            print(f"Database file {self.db_file} not found. Please run the expense tracker first.")
            return
            
        # Check if we can connect to the database
        try:
            conn = self.get_db_connection()
            conn.close()
        except sqlite3.Error:
            print("Error connecting to database. Starting with empty data.")

    def get_expenses(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses")
        expenses = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return expenses
    
    def get_categories(self):
        """Get all unique categories from expenses"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM expenses ORDER BY category")
        categories = [row['category'] for row in cursor.fetchall()]
        conn.close()
        return categories
    
    def get_category_totals(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT category, SUM(amount) as total
            FROM expenses
            GROUP BY category
            ORDER BY category
        ''')
        totals = {row['category']: row['total'] for row in cursor.fetchall()}
        conn.close()
        return totals
    
    def plot_expenses_by_category(self):
        """Create a pie chart of expenses by category"""
        category_totals = self.get_category_totals()
        
        if not category_totals:
            print("No expenses to analyze.")
            return
        
        # Filter out categories with 0 expenses
        filtered_categories = []
        filtered_totals = []
        
        for category, total in category_totals.items():
            if total > 0:
                filtered_categories.append(category)
                filtered_totals.append(total)
        
        plt.figure(figsize=(10, 7))
        plt.pie(filtered_totals, labels=filtered_categories, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title('Expenses by Category')
        plt.tight_layout()
        plt.savefig('expenses_by_category.png')
        plt.close()
        
        print("Chart saved as 'expenses_by_category.png'")
    
    def plot_monthly_expenses(self):
        """Create a bar chart of expenses by month"""
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
        
        if not monthly_expenses:
            print("No expenses to analyze.")
            return
        
        # Sort months chronologically
        sorted_months = sorted(monthly_expenses.keys())
        months = [datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in sorted_months]
        values = [monthly_expenses[m] for m in sorted_months]
        
        plt.figure(figsize=(12, 6))
        plt.bar(months, values, color='skyblue')
        plt.xlabel('Month')
        plt.ylabel('Total Expenses ($)')
        plt.title('Monthly Expenses')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('monthly_expenses.png')
        plt.close()
        
        print("Chart saved as 'monthly_expenses.png'")
    
    def plot_expense_trend(self):
        """Create a line chart showing expense trends over time"""
        expenses = self.get_expenses()
        
        if not expenses:
            print("No expenses to analyze.")
            return
        
        # Sort expenses by date
        sorted_expenses = sorted(expenses, key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d %H:%M:%S"))
        
        dates = [datetime.strptime(expense["date"], "%Y-%m-%d %H:%M:%S") for expense in sorted_expenses]
        amounts = [expense["amount"] for expense in sorted_expenses]
        
        # Calculate cumulative expenses
        cumulative = []
        total = 0
        for amount in amounts:
            total += amount
            cumulative.append(total)
        
        plt.figure(figsize=(12, 6))
        plt.plot(dates, cumulative, marker='o', linestyle='-', color='green')
        plt.xlabel('Date')
        plt.ylabel('Cumulative Expenses ($)')
        plt.title('Expense Trend Over Time')
        plt.gcf().autofmt_xdate()  # Auto-format the x-axis for dates
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig('expense_trend.png')
        plt.close()
        
        print("Chart saved as 'expense_trend.png'")
    
    def generate_monthly_report(self, year=None, month=None):
        """Generate a monthly expense report"""
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        
        # Convert to strings for SQLite query
        year_str = str(year)
        month_str = f"{month:02d}"
        date_pattern = f"{year_str}-{month_str}-%"
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Get monthly expenses
        cursor.execute('''
            SELECT * FROM expenses 
            WHERE date LIKE ?
            ORDER BY date
        ''', (date_pattern,))
        
        monthly_expenses = [dict(row) for row in cursor.fetchall()]
        
        if not monthly_expenses:
            print(f"No expenses found for {calendar.month_name[month]} {year}")
            conn.close()
            return
        
        # Calculate totals by category
        cursor.execute('''
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE date LIKE ?
            GROUP BY category
            ORDER BY total DESC
        ''', (date_pattern,))
        
        categories = {row['category']: row['total'] for row in cursor.fetchall()}
        
        # Get total for the month
        cursor.execute('''
            SELECT SUM(amount) as total
            FROM expenses
            WHERE date LIKE ?
        ''', (date_pattern,))
        
        result = cursor.fetchone()
        total = result['total'] or 0
        
        conn.close()
        
        # Print report
        print(f"\nExpense Report for {calendar.month_name[month]} {year}")
        print("=" * 40)
        print(f"Total Expenses: ${total:.2f}")
        print("\nBreakdown by Category:")
        for category, amount in categories.items():
            percentage = (amount / total) * 100
            print(f"{category}: ${amount:.2f} ({percentage:.1f}%)")
        
        print("\nDetailed Expenses:")
        for expense in monthly_expenses:
            date = datetime.strptime(expense["date"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            print(f"{date} - {expense['category']} - ${expense['amount']:.2f} - {expense['description']}")


def main():
    analyzer = ExpenseAnalyzer()
    
    while True:
        print("\nExpense Analyzer")
        print("1. Generate Expense Breakdown by Category (Pie Chart)")
        print("2. Generate Monthly Expenses Chart (Bar Chart)")
        print("3. Generate Expense Trend Over Time (Line Chart)")
        print("4. Generate Monthly Report")
        print("5. Exit")
        
        choice = input("Select an option: ")
        
        if choice == "1":
            analyzer.plot_expenses_by_category()
        
        elif choice == "2":
            analyzer.plot_monthly_expenses()
        
        elif choice == "3":
            analyzer.plot_expense_trend()
        
        elif choice == "4":
            year_input = input("Enter year (press Enter for current year): ")
            month_input = input("Enter month (1-12, press Enter for current month): ")
            
            try:
                year = int(year_input) if year_input.strip() else datetime.now().year
                month = int(month_input) if month_input.strip() else datetime.now().month
                
                if 1 <= month <= 12:
                    analyzer.generate_monthly_report(year, month)
                else:
                    print("Invalid month. Please enter a number between 1 and 12.")
            except ValueError:
                print("Invalid input. Please enter valid numbers.")
        
        elif choice == "5":
            print("Exiting Expense Analyzer.")
            break
        
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main() 