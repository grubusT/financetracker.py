# Expense Tracker

A simple application to track your expenses.

## Features

- Add expenses with categories and descriptions
- View all expenses
- View expenses by category
- Calculate total expenses
- Remove expenses
- Data persistence with SQLite database
- Data visualization with charts and reports
- Web interface for easier management

## Requirements

- Python 3.6 or higher
- Flask (for web interface)
- Matplotlib (for the expense analyzer)
- SQLite (included with Python)

To install the required packages:

```
pip install flask matplotlib
```

## How to Use

### Command-line Interface

1. Clone or download this repository
2. Navigate to the project directory
3. Run the expense tracker application:

```
python app.py
```

4. Run the expense analyzer (for visualizations and reports):

```
python expense_analyzer.py
```

### Web Interface

1. Clone or download this repository
2. Navigate to the project directory
3. Run the web application:

```
python app_web.py
```

4. Open your browser and navigate to:

```
http://localhost:5000
```

## Usage Guide

### Command-line Interface

#### Expense Tracker (app.py)

- Add expenses with amount, category, and description
- View all expenses or by category
- Calculate total expenses
- Remove expenses

#### Expense Analyzer (expense_analyzer.py)

- Generate pie charts of expenses by category
- Generate bar charts of monthly expenses
- Generate line charts of expense trends
- Create detailed monthly reports

### Web Interface (app_web.py)

The web interface provides a more user-friendly way to manage your expenses:

#### Dashboard
- View total expenses
- Quick add expense form
- Expense breakdown chart
- Recent expenses list

#### Expenses
- View all expenses in a table format
- Filter expenses by category
- Add new expenses
- Remove expenses

#### Analytics
- Visualize expenses by category (pie chart)
- View category breakdown with percentages
- Track monthly expenses (bar chart)
- See expense trends over time (line chart)

## Data Storage

All expense data is stored in a SQLite database file named `expenses.db` in the same directory as the application. The database has the following structure:

### Database Schema

#### Expenses Table
- `id` - Unique identifier (Primary Key, Auto Increment)
- `amount` - Expense amount (Real/Float)
- `category` - Expense category (Text)
- `description` - Optional description (Text)
- `date` - Timestamp when the expense was added (Text in YYYY-MM-DD HH:MM:SS format)

#### Categories Table
- `id` - Unique identifier (Primary Key, Auto Increment)
- `name` - Category name (Text, Unique)

Both the CLI and web interfaces use the same database file, so you can easily switch between them.

## Generated Charts

The expense analyzer generates the following chart files:
- `expenses_by_category.png` - Pie chart showing expenses by category
- `monthly_expenses.png` - Bar chart showing expenses by month
- `expense_trend.png` - Line chart showing expense trends over time 