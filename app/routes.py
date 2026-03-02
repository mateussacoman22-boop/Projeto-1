from collections import defaultdict
from datetime import date, datetime

from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import extract, func

from . import db
from .models import Budget, Category, FinancialRecord, User

PAYMENT_METHODS = ["credit card", "debit card", "pix", "cash", "bank transfer"]


def seed_default_categories(user):
    defaults = ["Rent", "Groceries", "Entertainment", "Salary", "Health", "Transport", "Investments"]
    for name in defaults:
        db.session.add(Category(name=name, user_id=user.id))
    db.session.commit()


def parse_month_year():
    today = date.today()
    month = int(request.args.get("month", today.month))
    year = int(request.args.get("year", today.year))
    return month, year


def month_name(month: int):
    return datetime(2000, month, 1).strftime("%B")


def init_routes(app):
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return render_template("index.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form["username"].strip()
            email = request.form["email"].strip().lower()
            password = request.form["password"]

            if User.query.filter((User.username == username) | (User.email == email)).first():
                flash("Username or email already exists.", "danger")
                return redirect(url_for("register"))

            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            seed_default_categories(user)
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form["email"].strip().lower()
            password = request.form["password"]
            user = User.query.filter_by(email=email).first()

            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for("dashboard"))

            flash("Invalid credentials.", "danger")

        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("index"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        month, year = parse_month_year()

        records = FinancialRecord.query.filter_by(user_id=current_user.id).all()
        monthly_records = [
            record
            for record in records
            if record.date.month == month and record.date.year == year
        ]

        income_total = sum(r.amount for r in monthly_records if r.kind == "income")
        expense_total = sum(r.amount for r in monthly_records if r.kind == "expense")
        balance_total = sum(r.amount if r.kind == "income" else -r.amount for r in records)

        prev_month = 12 if month == 1 else month - 1
        prev_year = year - 1 if month == 1 else year
        prev_records = [
            record
            for record in records
            if record.date.month == prev_month and record.date.year == prev_year
        ]
        prev_income = sum(r.amount for r in prev_records if r.kind == "income")
        prev_expense = sum(r.amount for r in prev_records if r.kind == "expense")

        expenses_by_category = defaultdict(float)
        for rec in monthly_records:
            if rec.kind == "expense":
                expenses_by_category[rec.category.name] += rec.amount

        monthly_trend = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
        for rec in records:
            key = rec.date.strftime("%Y-%m")
            monthly_trend[key][rec.kind] += rec.amount

        balance_evolution = []
        running_balance = 0
        for rec in sorted(records, key=lambda r: r.date):
            running_balance += rec.amount if rec.kind == "income" else -rec.amount
            balance_evolution.append({"date": rec.date.isoformat(), "balance": round(running_balance, 2)})

        budgets = Budget.query.filter_by(user_id=current_user.id, month=month, year=year).all()
        budget_status = []
        for budget in budgets:
            spent = expenses_by_category.get(budget.category.name, 0)
            percentage = (spent / budget.limit_amount * 100) if budget.limit_amount else 0
            budget_status.append(
                {
                    "category": budget.category.name,
                    "limit": budget.limit_amount,
                    "spent": spent,
                    "percentage": round(percentage, 2),
                    "alert": "Exceeded" if percentage > 100 else "Near limit" if percentage >= 80 else "On track",
                }
            )

        return render_template(
            "dashboard.html",
            month=month,
            year=year,
            month_label=month_name(month),
            income_total=round(income_total, 2),
            expense_total=round(expense_total, 2),
            balance_total=round(balance_total, 2),
            prev_income=round(prev_income, 2),
            prev_expense=round(prev_expense, 2),
            records=monthly_records,
            categories=Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all(),
            payment_methods=PAYMENT_METHODS,
            expenses_by_category=dict(expenses_by_category),
            monthly_trend=dict(monthly_trend),
            balance_evolution=balance_evolution,
            budget_status=budget_status,
        )

    @app.route("/records/new", methods=["POST"])
    @login_required
    def create_record():
        record = FinancialRecord(
            date=datetime.strptime(request.form["date"], "%Y-%m-%d").date(),
            amount=float(request.form["amount"]),
            category_id=int(request.form["category_id"]),
            kind=request.form["kind"],
            recurrence_type=request.form["recurrence_type"],
            payment_method=request.form["payment_method"],
            notes=request.form.get("notes", ""),
            user_id=current_user.id,
        )
        db.session.add(record)
        db.session.commit()
        flash("Record saved.", "success")
        return redirect(url_for("dashboard", month=record.date.month, year=record.date.year))

    @app.route("/records/<int:record_id>/edit", methods=["POST"])
    @login_required
    def edit_record(record_id):
        record = FinancialRecord.query.filter_by(id=record_id, user_id=current_user.id).first_or_404()
        record.date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
        record.amount = float(request.form["amount"])
        record.category_id = int(request.form["category_id"])
        record.kind = request.form["kind"]
        record.recurrence_type = request.form["recurrence_type"]
        record.payment_method = request.form["payment_method"]
        record.notes = request.form.get("notes", "")
        db.session.commit()
        flash("Record updated.", "success")
        return redirect(url_for("dashboard", month=record.date.month, year=record.date.year))

    @app.route("/records/<int:record_id>/delete", methods=["POST"])
    @login_required
    def delete_record(record_id):
        record = FinancialRecord.query.filter_by(id=record_id, user_id=current_user.id).first_or_404()
        month, year = record.date.month, record.date.year
        db.session.delete(record)
        db.session.commit()
        flash("Record deleted.", "info")
        return redirect(url_for("dashboard", month=month, year=year))

    @app.route("/categories", methods=["POST"])
    @login_required
    def add_category():
        name = request.form["name"].strip()
        if name:
            db.session.add(Category(name=name, user_id=current_user.id))
            db.session.commit()
            flash("Category created.", "success")
        return redirect(url_for("dashboard"))

    @app.route("/budgets", methods=["POST"])
    @login_required
    def set_budget():
        month = int(request.form["month"])
        year = int(request.form["year"])
        category_id = int(request.form["category_id"])
        limit_amount = float(request.form["limit_amount"])

        budget = Budget.query.filter_by(
            user_id=current_user.id,
            month=month,
            year=year,
            category_id=category_id,
        ).first()
        if budget:
            budget.limit_amount = limit_amount
        else:
            budget = Budget(
                month=month,
                year=year,
                category_id=category_id,
                limit_amount=limit_amount,
                user_id=current_user.id,
            )
            db.session.add(budget)

        db.session.commit()
        flash("Budget updated.", "success")
        return redirect(url_for("dashboard", month=month, year=year))

    @app.route("/api/annual-summary")
    @login_required
    def annual_summary():
        year = int(request.args.get("year", date.today().year))
        monthly = (
            db.session.query(
                extract("month", FinancialRecord.date).label("month"),
                FinancialRecord.kind,
                func.sum(FinancialRecord.amount),
            )
            .filter(extract("year", FinancialRecord.date) == year, FinancialRecord.user_id == current_user.id)
            .group_by("month", FinancialRecord.kind)
            .all()
        )

        data = {m: {"income": 0, "expense": 0} for m in range(1, 13)}
        for month_num, kind, total in monthly:
            data[int(month_num)][kind] = float(total)

        return jsonify({"year": year, "months": data})
