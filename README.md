# FinanceFlow - Personal & Family Financial Control System

FinanceFlow is a complete, modern, responsive, and web-based financial control system for personal and family money management.

## Features
- User authentication (register/login/logout) with user-scoped data isolation.
- Income and expense records with:
  - Date
  - Amount
  - Category
  - Type (fixed/variable)
  - Payment method
  - Notes
- Category management.
- Record editing and deletion.
- Filters by month and year.
- Advanced dashboard:
  - Current total balance
  - Monthly income and expense totals
  - Current vs previous month comparison
  - Interactive charts (Chart.js):
    - Pie chart (expenses by category)
    - Bar chart (monthly income vs expenses)
    - Line chart (balance evolution)
    - Doughnut chart (spending percentage by category)
- Budget planning:
  - Monthly category limits
  - Visual alerts (on track / near limit / exceeded)
- Theme toggle (light/dark).
- Annual summary API endpoint (`/api/annual-summary`).

## Project Structure

```text
Projeto-1/
├── app/
│   ├── __init__.py        # Flask app factory, DB and login initialization
│   ├── models.py          # SQLAlchemy models (User, Category, FinancialRecord, Budget)
│   └── routes.py          # Routes, controllers and dashboard aggregation logic
├── static/
│   ├── css/
│   │   └── styles.css     # Responsive and modern styling + dark theme
│   └── js/
│       └── app.js         # Theme toggle and chart initialization
├── templates/
│   ├── base.html          # Shared layout
│   ├── index.html         # Landing page
│   ├── login.html         # Authentication screen
│   ├── register.html      # Registration screen
│   └── dashboard.html     # Main dashboard with forms, table and charts
├── run.py                 # Entry point
├── requirements.txt       # Python dependencies
└── README.md              # Documentation
```

## Local Run Instructions

1. Create and activate virtualenv:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run app:
   ```bash
   python run.py
   ```
4. Access in browser:
   - `http://127.0.0.1:5000`

## Notes
- SQLite database is created automatically in `instance/finance.db`.
- In production, replace `SECRET_KEY` and use a production-grade database and WSGI server.

