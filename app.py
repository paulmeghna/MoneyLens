# ============================================================
# IMPORTS
# ============================================================

# Flask:
# Flask -> creates our web application
# render_template -> loads HTML files from the templates folder
# request -> reads data submitted by forms
from flask import Flask, render_template, request

# Import SQLAlchemy database object and User model
from models import db, User

# Import our application configuration
from config import Config

# Flask-Login:
# LoginManager -> manages authentication
# login_user -> logs a user in
# login_required -> protects routes from unauthenticated users
# current_user -> gives access to the currently logged-in user
# logout_user -> logs the current user out
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    current_user,
    logout_user
)

# Werkzeug security:
# generate_password_hash -> securely hashes a password
# check_password_hash -> checks a password against its stored hash
from werkzeug.security import generate_password_hash, check_password_hash


# ============================================================
# CREATE FLASK APPLICATION
# ============================================================

# Create the Flask application object
app = Flask(__name__)

# Load configuration from the Config class
app.config.from_object(Config)


# ============================================================
# INITIALIZE DATABASE
# ============================================================

# Connect SQLAlchemy with our Flask application
db.init_app(app)


# ============================================================
# INITIALIZE FLASK-LOGIN
# ============================================================

# Create the single LoginManager object for the application
login_manager = LoginManager()

# Connect LoginManager with Flask
login_manager.init_app(app)

# If a user tries to access a protected page without logging in,
# Flask-Login will send them to the /login route
login_manager.login_view = "login"


# ============================================================
# USER LOADER
# ============================================================

# Flask-Login uses this function to reload a logged-in user
# from the database using the user ID stored in the session.
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

# Create the database tables if they do not already exist.
# This uses the database configuration from config.py.
with app.app_context():
    db.create_all()


# ============================================================
# REGISTRATION ROUTE
# ============================================================

# This route handles both:
# GET  -> show the registration page
# POST -> process the registration form
@app.route("/register", methods=["GET", "POST"])
def register():

    # Check whether the registration form was submitted
    if request.method == "POST":

        # Read values entered into the form
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # --------------------------------------------------------
        # CHECK FOR DUPLICATE EMAIL
        # --------------------------------------------------------

        # Check whether an account with this email already exists
        existing_user = User.query.filter_by(email=email).first()

        # If the email is already registered, stop registration
        if existing_user:
            return "Email already registered."

        # --------------------------------------------------------
        # HASH PASSWORD
        # --------------------------------------------------------

        # Never store the user's plain-text password.
        # Convert it into a secure password hash instead.
        password_hash = generate_password_hash(password)

        # --------------------------------------------------------
        # CREATE USER OBJECT
        # --------------------------------------------------------

        # Create a new User object using the submitted data
        user = User(
            name=name,
            email=email,
            password_hash=password_hash
        )

        # Add the new user to the database session
        db.session.add(user)

        # Permanently save the new user to the database
        db.session.commit()

        # Temporary success response for our current testing stage
        return "Registration successful!"

    # If the request is GET, show the registration page
    return render_template("register.html")


# ============================================================
# LOGIN ROUTE
# ============================================================

# This route handles:
# GET  -> show the login page
# POST -> process login credentials
@app.route("/login", methods=["GET", "POST"])
def login():

    # Check whether the login form was submitted
    if request.method == "POST":

        # Read email and password from the form
        email = request.form["email"]
        password = request.form["password"]

        # Find the user with the submitted email
        user = User.query.filter_by(email=email).first()

        # Check:
        # 1. A user with that email exists
        # 2. The entered password matches the stored password hash
        if user and check_password_hash(user.password_hash, password):

            # Create the authenticated login session
            login_user(user)

            # Temporary success response for our testing stage
            return "Login successful!"

        # Generic error message for invalid credentials
        # We do not reveal whether the email exists.
        return "Invalid email or password."

    # If the request is GET, show the login page
    return render_template("login.html")


# ============================================================
# HOME ROUTE
# ============================================================

# Public home page
@app.route("/")
def home():
    return render_template("index.html")


# ============================================================
# PROTECTED DASHBOARD ROUTE
# ============================================================

# @login_required means only authenticated users
# are allowed to access this page.
@app.route("/dashboard")
@login_required
def dashboard():

    # current_user represents the currently logged-in user
    return f"Welcome, {current_user.name}!"


# ============================================================
# LOGOUT ROUTE
# ============================================================

# @login_required ensures only logged-in users can log out
@app.route("/logout")
@login_required
def logout():

    # End the current user's authenticated session
    logout_user()

    # Temporary response for our testing stage
    return "Logged out successfully!"


# ============================================================
# RUN THE APPLICATION
# ============================================================

# This block runs only when app.py is executed directly.
if __name__ == "__main__":

    # Start the Flask development server
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )