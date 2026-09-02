
from datetime import datetime

from flask import Flask, render_template, request, redirect
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    current_user,
    logout_user,
)
from flask_migrate import Migrate
from sqlalchemy import extract, func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import db, User, Transaction, Budget


# ------------------------------------------------------------
# Application setup
# ------------------------------------------------------------

app = Flask(__name__)
app.config.from_object(Config)

# Connect SQLAlchemy to the Flask application.
db.init_app(app)

# Configure Flask-Migrate for database schema changes.
migrate = Migrate(app, db)

# Configure Flask-Login.
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    """Load the logged-in user from the database."""
    return db.session.get(User, int(user_id))


# Create database tables if they do not already exist.
with app.app_context():
    db.create_all()


# ------------------------------------------------------------
# Authentication routes
# ------------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Validate required fields.
        if not name:
            return "Name is required.", 400

        if not email:
            return "Email is required.", 400

        if not password:
            return "Password is required.", 400

        # Prevent duplicate email registration.
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already registered.", 400

        # Hash the password before storing it.
        password_hash = generate_password_hash(password)

        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
        )

        db.session.add(user)
        db.session.commit()

        return "Registration successful!"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)

            # Return the user to the page they originally requested,
            # or to the home page if there was no protected page.
            return redirect(request.args.get("next") or "/")

        return "Invalid email or password.", 401

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return "Logged out successfully."


# ------------------------------------------------------------
# Main pages
# ------------------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
@login_required
def dashboard():
    view = request.args.get("view", "month")
    month = request.args.get(
        "month",
        datetime.now().month,
        type=int
    )
    year = request.args.get(
        "year",
        datetime.now().year,
        type=int
    )

    # Validate the selected month only when Month view is used.
    if view == "month" and (month < 1 or month > 12):
        return "Month must be between 1 and 12.", 400

    # Validate the selected year for Month and Year views.
    if view in ("month", "year") and year < 2020:
        return "Year must be 2020 or later.", 400

    # This list will contain the 12-month breakdown for Year view.
    monthly_breakdown = []

    # Start with transactions belonging ONLY to the logged-in user.
    income_query = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "income"
    )

    expense_query = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense"
    )

    # --------------------------------------------------------
    # Apply date filters based on the selected dashboard view.
    # --------------------------------------------------------

    # Month view: selected month and year.
    if view == "month":
        income_query = income_query.filter(
            extract("month", Transaction.date) == month,
            extract("year", Transaction.date) == year
        )

        expense_query = expense_query.filter(
            extract("month", Transaction.date) == month,
            extract("year", Transaction.date) == year
        )

    # Year view: selected year only.
    elif view == "year":
        income_query = income_query.filter(
            extract("year", Transaction.date) == year
        )

        expense_query = expense_query.filter(
            extract("year", Transaction.date) == year
        )

        # Calculate income and expense for each month
        # of the selected year.
        for selected_month in range(1, 13):
            monthly_income = income_query.filter(
                extract("month", Transaction.date) == selected_month
            ).with_entities(
                func.sum(Transaction.amount)
            ).scalar() or 0

            monthly_expense = expense_query.filter(
                extract("month", Transaction.date) == selected_month
            ).with_entities(
                func.sum(Transaction.amount)
            ).scalar() or 0

            monthly_breakdown.append({
                "month": selected_month,
                "income": monthly_income,
                "expense": monthly_expense
            })

    # All Time view: no date filter is applied.
    elif view == "all":
        pass

    # Reject unsupported dashboard views.
    else:
        return "Invalid dashboard view.", 400

    # --------------------------------------------------------
    # Basic financial calculations.
    # --------------------------------------------------------

    # Calculate total income for the selected view.
    total_income = income_query.with_entities(
        func.sum(Transaction.amount)
    ).scalar() or 0

    # Calculate total expense for the selected view.
    total_expense = expense_query.with_entities(
        func.sum(Transaction.amount)
    ).scalar() or 0

    # Balance is income minus expense.
    balance = total_income - total_expense

    # Savings is the amount remaining after expenses.
    savings = total_income - total_expense

    # Savings rate shows what percentage of income remains.
    # When income is zero, return 0 to avoid division by zero.
    savings_rate = (
        (savings / total_income) * 100
        if total_income != 0
        else 0
    )

    # --------------------------------------------------------
    # Expense analytics.
    # --------------------------------------------------------

    # Calculate total expenses for each category.
    #
    # This query is restricted to the logged-in user and
    # will use the same date range as the selected dashboard view.
    category_expenses_query = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense"
    )

    # Month view: only expenses from the selected month/year.
    if view == "month":
        category_expenses_query = category_expenses_query.filter(
            extract("month", Transaction.date) == month,
            extract("year", Transaction.date) == year
        )

    # Year view: only expenses from the selected year.
    elif view == "year":
        category_expenses_query = category_expenses_query.filter(
            extract("year", Transaction.date) == year
        )

    # All Time view keeps all of the user's expenses.

    # Group expenses by category and show the highest
    # spending categories first.
    category_expenses = category_expenses_query.group_by(
        Transaction.category
    ).order_by(
        func.sum(Transaction.amount).desc()
    ).all()

    top_expense_category = category_expenses[0] if category_expenses else None
    

    # Send all calculated values to the dashboard template.
    return render_template(
        "dashboard.html",
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        savings=savings,
        savings_rate=savings_rate,
        category_expenses=category_expenses,
        top_expense_category=top_expense_category,
        view=view,
        month=month,
        year=year,
        monthly_breakdown=monthly_breakdown
    )


# ------------------------------------------------------------
# Transaction routes
# ------------------------------------------------------------

@app.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions():
    if request.method == "POST":
        transaction_type = request.form.get(
            "type",
            ""
        ).strip().lower()

        category = request.form.get(
            "category",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        # Only income and expense transactions are allowed.
        if transaction_type not in ("income", "expense"):
            return (
                "Transaction type must be income or expense.",
                400
            )

        # Category is required.
        if not category:
            return "Category is required.", 400

        # Validate the transaction amount.
        try:
            amount = float(
                request.form.get("amount", "")
            )
        except (ValueError, TypeError):
            return "Amount must be a valid number.", 400

        if amount <= 0:
            return "Amount must be greater than 0.", 400

        # Validate the transaction date.
        try:
            transaction_date = datetime.strptime(
                request.form.get("date", ""),
                "%Y-%m-%d"
            ).date()
        except (ValueError, TypeError):
            return "Date must be valid.", 400

        # Create the transaction for the currently
        # logged-in user.
        transaction = Transaction(
            user_id=current_user.id,
            type=transaction_type,
            amount=amount,
            category=category,
            description=description,
            date=transaction_date,
        )

        db.session.add(transaction)
        db.session.commit()

        # POST-Redirect-GET prevents duplicate submissions
        # when the browser refreshes the page.
        return redirect("/transactions")

    # Show ONLY transactions owned by the logged-in user.
    transactions = Transaction.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Transaction.date.desc()
    ).all()

    return render_template(
        "transactions.html",
        transactions=transactions
    )


@app.route(
    "/transactions/<int:transaction_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_transaction(transaction_id):
    # Find the transaction AND verify ownership.
    #
    # This prevents a user from editing another user's
    # transaction by manually changing the URL ID.
    transaction = Transaction.query.filter_by(
        id=transaction_id,
        user_id=current_user.id
    ).first()

    if transaction is None:
        return "Transaction not found.", 404

    if request.method == "POST":
        transaction_type = request.form.get(
            "type",
            ""
        ).strip().lower()

        category = request.form.get(
            "category",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        # Validate transaction type.
        if transaction_type not in ("income", "expense"):
            return (
                "Transaction type must be income or expense.",
                400
            )

        # Category is required.
        if not category:
            return "Category is required.", 400

        # Validate the transaction amount.
        try:
            amount = float(
                request.form.get("amount", "")
            )
        except (ValueError, TypeError):
            return "Amount must be a valid number.", 400

        if amount <= 0:
            return "Amount must be greater than 0.", 400

        # Validate the transaction date.
        try:
            transaction_date = datetime.strptime(
                request.form.get("date", ""),
                "%Y-%m-%d"
            ).date()
        except (ValueError, TypeError):
            return "Date must be valid.", 400

        # Update the existing transaction.
        transaction.type = transaction_type
        transaction.amount = amount
        transaction.category = category
        transaction.description = description
        transaction.date = transaction_date

        db.session.commit()

        return redirect("/transactions")

    return render_template(
        "edit_transaction.html",
        transaction=transaction
    )


@app.route(
    "/transactions/<int:transaction_id>/delete",
    methods=["POST"]
)
@login_required
def delete_transaction(transaction_id):
    # Find the transaction AND verify ownership.
    #
    # This prevents one user from deleting another user's
    # transaction by changing the transaction ID.
    transaction = Transaction.query.filter_by(
        id=transaction_id,
        user_id=current_user.id
    ).first()

    if transaction is None:
        return "Transaction not found.", 404

    db.session.delete(transaction)
    db.session.commit()

    return redirect("/transactions")


# ------------------------------------------------------------
# Budget routes
# ------------------------------------------------------------

@app.route("/budgets", methods=["GET", "POST"])
@login_required
def budgets():
    if request.method == "POST":
        category = request.form.get(
            "category",
            ""
        ).strip()

        # Validate category.
        if not category:
            return "Category is required.", 400

        # Validate month.
        try:
            month = int(
                request.form.get("month", "")
            )
        except (ValueError, TypeError):
            return "Month must be a valid number.", 400

        if month < 1 or month > 12:
            return "Month must be between 1 and 12.", 400

        # Validate year.
        try:
            year = int(
                request.form.get("year", "")
            )
        except (ValueError, TypeError):
            return "Year must be a valid number.", 400

        if year < 2020:
            return "Year must be 2020 or later.", 400

        # Validate budget amount.
        try:
            amount = float(
                request.form.get("amount", "")
            )
        except (ValueError, TypeError):
            return "Amount must be a valid number.", 400

        if amount <= 0:
            return "Amount must be greater than 0.", 400

        # Create a budget belonging to the logged-in user.
        budget = Budget(
            user_id=current_user.id,
            month=month,
            year=year,
            category=category,
            amount=amount
        )

        db.session.add(budget)

        try:
            db.session.commit()

        except IntegrityError:
            # Roll back the failed transaction so the SQLAlchemy
            # session can safely be used again.
            db.session.rollback()

            # The Budget model has a unique constraint on
            # user + category + month + year.
            return (
                "A budget already exists for this category, "
                "month, and year."
            ), 400

        # POST-Redirect-GET prevents duplicate budgets
        # when the browser page is refreshed.
        return redirect("/budgets")

    # Get only budgets belonging to the logged-in user.
    budgets = Budget.query.filter_by(
        user_id=current_user.id
    ).all()

    # Calculate spending information for every budget.
    for budget in budgets:

        # Sum only expense transactions that belong to:
        # 1. the current user
        # 2. the same category
        # 3. the same month
        # 4. the same year
        spent = db.session.query(
            func.sum(Transaction.amount)
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.category == budget.category,
            Transaction.type == "expense",
            extract("month", Transaction.date) == budget.month,
            extract("year", Transaction.date) == budget.year
        ).scalar() or 0

        # Calculate the amount still available.
        remaining = budget.amount - spent

        # Calculate how much of the budget has been used.
        utilization = (
            spent / budget.amount
        ) * 100

        # Determine whether the budget has been exceeded.
        if remaining < 0:
            status = "Overspent"
        else:
            status = "Within Budget"

        # These are calculated values only.
        # They are not stored in the Budget database table.
        budget.spent = spent
        budget.remaining = remaining
        budget.utilization = utilization
        budget.status = status

    return render_template(
        "budgets.html",
        budgets=budgets
    )


@app.route(
    "/budgets/<int:budget_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_budget(budget_id):
    # Find the budget AND verify ownership.
    budget = Budget.query.filter_by(
        id=budget_id,
        user_id=current_user.id
    ).first()

    if budget is None:
        return "Budget not found.", 404

    if request.method == "POST":
        category = request.form.get(
            "category",
            ""
        ).strip()

        # Validate category.
        if not category:
            return "Category is required.", 400

        # Validate month.
        try:
            month = int(
                request.form.get("month", "")
            )
        except (ValueError, TypeError):
            return "Month must be a valid number.", 400

        if month < 1 or month > 12:
            return "Month must be between 1 and 12.", 400

        # Validate year.
        try:
            year = int(
                request.form.get("year", "")
            )
        except (ValueError, TypeError):
            return "Year must be a valid number.", 400

        if year < 2020:
            return "Year must be 2020 or later.", 400

        # Validate budget amount.
        try:
            amount = float(
                request.form.get("amount", "")
            )
        except (ValueError, TypeError):
            return "Amount must be a valid number.", 400

        if amount <= 0:
            return "Amount must be greater than 0.", 400

        # Update the existing budget.
        budget.category = category
        budget.month = month
        budget.year = year
        budget.amount = amount

        try:
            db.session.commit()

        except IntegrityError:
            # Roll back the failed update so the SQLAlchemy
            # session remains usable.
            db.session.rollback()

            return (
                "A budget already exists for this category, "
                "month, and year."
            ), 400

        return redirect("/budgets")

    return render_template(
        "edit_budget.html",
        budget=budget
    )


@app.route(
    "/budgets/<int:budget_id>/delete",
    methods=["POST"]
)
@login_required
def delete_budget(budget_id):
    # Find the budget AND verify ownership.
    budget = Budget.query.filter_by(
        id=budget_id,
        user_id=current_user.id
    ).first()

    if budget is None:
        return "Budget not found.", 404

    db.session.delete(budget)
    db.session.commit()

    return redirect("/budgets")


# ------------------------------------------------------------
# Run application
# ------------------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000,
    )

