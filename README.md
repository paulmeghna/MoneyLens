# 💰 MoneyLens

A full-stack personal finance and expense management application built with Flask. MoneyLens is designed to help users manage their income, expenses, budgets, and financial activity through a secure and user-friendly web application.

## ✨ Features

### Currently Implemented

* User registration and login
* Secure password hashing
* User authentication and sessions
* Protected user dashboard
* Logout functionality
* Duplicate email protection

### Planned

* Income and expense management
* Budget management
* Financial summaries and insights
* Charts and analytics
* Production deployment

## 🛠️ Technologies Used

* **Python** — Backend programming language
* **Flask** — Web application framework
* **Flask-Login** — User authentication and session management
* **SQLAlchemy** — Database ORM
* **SQLite** — Development database
* **HTML** — Web page structure
* **CSS** — Styling and layout
* **JavaScript** — Frontend interactivity
* **Git & GitHub** — Version control and project hosting

## 📁 Project Structure

```text
MoneyLens/
├── app.py                  # Main Flask application
├── config.py               # Application configuration
├── models.py               # Database models
├── requirements.txt        # Python dependencies
├── .gitignore              # Files ignored by Git
├── static/
│   ├── css/
│   │   └── style.css       # Application styling
│   └── js/
│       └── main.js         # Frontend JavaScript
├── templates/
│   ├── base.html           # Base template
│   ├── index.html          # Home page
│   ├── login.html          # Login page
│   └── register.html       # Registration page
├── instance/
│   └── database.db         # Local development database
└── venv/                   # Python virtual environment
```

## 🚀 How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/paulmeghna/MoneyLens.git
cd MoneyLens
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows PowerShell:**

```powershell
venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
python app.py
```

### 6. Open the application

Visit:

```text
http://127.0.0.1:5000
```
