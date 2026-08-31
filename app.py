
from flask import Flask, render_template, request
from datetime import datetime
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    current_user,
    logout_user,
)
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import db, User, Transaction


# ------------------------------------------------------------
# Application setup
# ------------------------------------------------------------

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

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
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already registered."

        password_hash = generate_password_hash(password)

        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
        )

        db.session.add(user)
        db.session.commit()

        return "Registration successful!"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return "Login successful!"

        return "Invalid email or password."

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
    return f"Welcome, {current_user.name}!"


# ------------------------------------------------------------
# Transaction routes
# ------------------------------------------------------------

@app.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions():
    if request.method == "POST":
        print("POST REQUEST RECEIVED")

        transaction_type = request.form["type"]

        try:
            amount = float(request.form["amount"])
        except ValueError:
            return "Amount must be a valid number."

        if amount <= 0:
            return "Amount must be greater than 0."

        category = request.form["category"]
        description = request.form["description"]
        date = datetime.strptime(
            request.form["date"],
            "%Y-%m-%d"
        ).date()

        transaction = Transaction(
            user_id=current_user.id,
            type=transaction_type,
            amount=float(amount),
            category=category,
            description=description,
            date=date,
        )

        db.session.add(transaction)
        db.session.commit()

    transactions = Transaction.query.filter_by(
        user_id=current_user.id
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
    transaction = Transaction.query.filter_by(
        id=transaction_id,
        user_id=current_user.id
    ).first()

    if transaction is None:
        return "Transaction not found."

    if request.method == "POST":
        transaction.type = request.form["type"]

        try:
            amount = float(request.form["amount"])
        except ValueError:
            return "Amount must be a valid number."

        if amount <= 0:
            return "Amount must be greater than 0."

        transaction.amount = amount
        transaction.category = request.form["category"]
        transaction.description = request.form["description"]
        try:
            transaction.date = datetime.strptime(
                request.form["date"],
                "%Y-%m-%d"
            ).date()
        except ValueError:
            return "Date must be valid."

        db.session.commit()

    return render_template("edit_transaction.html", transaction=transaction)

@app.route(
    "/transactions/<int:transaction_id>/delete",
    methods=["POST"]
)
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.filter_by(
        id=transaction_id,
        user_id=current_user.id
    ).first()

    if transaction is None:
        return "Transaction not found."

    db.session.delete(transaction)
    db.session.commit()

    return render_template(
        "transactions.html",
        transactions=Transaction.query.filter_by(
            user_id=current_user.id
        ).all()
    )


# -----------------------------------------------------------——
# Run application
# ------------------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000,
    )

