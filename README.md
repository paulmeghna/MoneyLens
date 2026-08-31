# 💰 MoneyLens

**MoneyLens** is a full-stack personal finance and expense management web application built with Flask.

It is designed to help users manage their financial activity through a secure and user-friendly web application.

> 🚧 **Project Status:** In Development

## ✨ Features

### Currently Implemented

- User registration and login
- Secure password hashing
- User authentication and sessions
- Protected user dashboard
- Logout functionality
- Duplicate email protection
- Income and expense management
- Transaction creation
- Transaction viewing
- Transaction editing
- Transaction deletion
- User-specific transaction access
- Basic transaction validation

### Planned

- Budget management
- Financial summaries and insights
- Charts and analytics
- Production deployment

## 🛠️ Technologies Used

- **Python** — Backend programming language
- **Flask** — Web application framework
- **Flask-Login** — User authentication and session management
- **SQLAlchemy** — Database ORM
- **SQLite** — Development database
- **HTML** — Web page structure
- **CSS** — Styling and layout
- **JavaScript** — Frontend interactivity
- **Git & GitHub** — Version control and project hosting

## 📁 Project Structure

```text
MoneyLens/

├── app.py                     # Main Flask application
├── config.py                  # Application configuration
├── models.py                  # Database models
├── requirements.txt           # Python dependencies
├── .gitignore                 # Files ignored by Git
├── static/
│   ├── css/
│   │   └── style.css          # Application styling
│   └── js/
│       └── main.js            # Frontend JavaScript
└── templates/
    ├── base.html              # Base template
    ├── index.html             # Home page
    ├── login.html             # Login page
    ├── register.html          # Registration page
    ├── transactions.html      # Transaction management page
    └── edit_transaction.html  # Edit transaction page