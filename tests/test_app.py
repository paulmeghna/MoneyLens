from models import User, Transaction, Budget


def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200


def test_login_page(client):
    response = client.get("/login")

    assert response.status_code == 200


def test_register_page(client):
    response = client.get("/register")

    assert response.status_code == 200


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_transactions_requires_login(client):
    response = client.get("/transactions")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_budgets_requires_login(client):
    response = client.get("/budgets")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_logout_requires_login(client):
    response = client.get("/logout")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_register_user(client):
    response = client.post(
        "/register",
        data={
            "name": "Test User",
            "email": "test@gmail.com",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 200


def test_duplicate_email_registration(client):
    first_response = client.post(
        "/register",
        data={
            "name": "First User",
            "email": "same@gmail.com",
            "password": "TestPassword123",
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/register",
        data={
            "name": "Second User",
            "email": "same@gmail.com",
            "password": "TestPassword456",
        },
    )

    assert second_response.status_code == 400
    assert b"already registered" in second_response.data


def test_successful_login(client):
    client.post(
        "/register",
        data={
            "name": "Login User",
            "email": "login@gmail.com",
            "password": "TestPassword123",
        },
    )

    response = client.post(
        "/login",
        data={
            "email": "login@gmail.com",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]


def test_invalid_login(client):
    client.post(
        "/register",
        data={
            "name": "Login User",
            "email": "wrong@gmail.com",
            "password": "TestPassword123",
        },
    )

    response = client.post(
        "/login",
        data={
            "email": "wrong@gmail.com",
            "password": "WrongPassword",
        },
    )

    assert response.status_code == 401
    assert b"Invalid email or password" in response.data


def test_two_users_are_separate(client):
    client.post(
        "/register",
        data={
            "name": "User A",
            "email": "usera@gmail.com",
            "password": "Password123",
        },
    )

    client.post(
        "/register",
        data={
            "name": "User B",
            "email": "userb@gmail.com",
            "password": "Password123",
        },
    )

    users = User.query.all()

    assert len(users) == 2
    assert users[0].email != users[1].email


def test_user_a_owns_transaction(client):
    client.post(
        "/register",
        data={
            "name": "User A",
            "email": "usera@gmail.com",
            "password": "Password123",
        },
    )

    user_a = User.query.filter_by(
        email="usera@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user_a.id)

    response = client.post(
        "/transactions",
        data={
            "type": "expense",
            "amount": "100",
            "category": "Food",
            "description": "User A transaction",
            "date": "2026-09-06",
        },
    )

    assert response.status_code == 302

    transaction = Transaction.query.first()

    assert transaction is not None
    assert transaction.user_id == user_a.id


def test_user_b_cannot_edit_user_a_transaction(client):
    client.post(
        "/register",
        data={
            "name": "User A",
            "email": "usera@gmail.com",
            "password": "Password123",
        },
    )

    user_a = User.query.filter_by(
        email="usera@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user_a.id)

    client.post(
        "/transactions",
        data={
            "type": "expense",
            "amount": "100",
            "category": "Food",
            "description": "User A transaction",
            "date": "2026-09-06",
        },
    )

    transaction = Transaction.query.first()

    client.get("/logout")

    client.post(
        "/register",
        data={
            "name": "User B",
            "email": "userb@gmail.com",
            "password": "Password123",
        },
    )

    user_b = User.query.filter_by(
        email="userb@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user_b.id)

    response = client.get(
        f"/transactions/{transaction.id}/edit"
    )

    assert response.status_code == 404


def test_user_b_cannot_delete_user_a_transaction(client):
    client.post(
        "/register",
        data={
            "name": "User A",
            "email": "usera@gmail.com",
            "password": "Password123",
        },
    )

    user_a = User.query.filter_by(
        email="usera@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user_a.id)

    client.post(
        "/transactions",
        data={
            "type": "expense",
            "amount": "100",
            "category": "Food",
            "description": "User A transaction",
            "date": "2026-09-06",
        },
    )

    transaction = Transaction.query.first()

    client.get("/logout")

    client.post(
        "/register",
        data={
            "name": "User B",
            "email": "userb@gmail.com",
            "password": "Password123",
        },
    )

    user_b = User.query.filter_by(
        email="userb@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user_b.id)

    response = client.post(
        f"/transactions/{transaction.id}/delete"
    )

    assert response.status_code == 404
    assert Transaction.query.first() is not None


def test_user_b_cannot_edit_user_a_budget(client):
    client.post(
        "/register",
        data={
            "name": "User A",
            "email": "usera@gmail.com",
            "password": "Password123",
        },
    )

    user_a = User.query.filter_by(
        email="usera@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user_a.id)

    client.post(
        "/budgets",
        data={
            "category": "Food",
            "month": "9",
            "year": "2026",
            "amount": "500",
        },
    )

    budget = Budget.query.first()

    client.get("/logout")

    client.post(
        "/register",
        data={
            "name": "User B",
            "email": "userb@gmail.com",
            "password": "Password123",
        },
    )

    user_b = User.query.filter_by(
        email="userb@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user_b.id)

    response = client.get(
        f"/budgets/{budget.id}/edit"
    )

    assert response.status_code == 404


def test_user_b_cannot_delete_user_a_budget(client):
    client.post(
        "/register",
        data={
            "name": "User A",
            "email": "usera@gmail.com",
            "password": "Password123",
        },
    )

    user_a = User.query.filter_by(
        email="usera@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user_a.id)

    client.post(
        "/budgets",
        data={
            "category": "Food",
            "month": "9",
            "year": "2026",
            "amount": "500",
        },
    )

    budget = Budget.query.first()

    client.get("/logout")

    client.post(
        "/register",
        data={
            "name": "User B",
            "email": "userb@gmail.com",
            "password": "Password123",
        },
    )

    user_b = User.query.filter_by(
        email="userb@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user_b.id)

    response = client.post(
        f"/budgets/{budget.id}/delete"
    )

    assert response.status_code == 404
    assert Budget.query.first() is not None


def test_user_b_sees_only_own_transactions(client):
    client.post(
        "/register",
        data={
            "name": "User A",
            "email": "usera@gmail.com",
            "password": "Password123",
        },
    )

    user_a = User.query.filter_by(
        email="usera@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user_a.id)

    client.post(
        "/transactions",
        data={
            "type": "expense",
            "amount": "100",
            "category": "Food",
            "description": "UserA_Private_Transaction",
            "date": "2026-09-06",
        },
    )

    client.get("/logout")

    client.post(
        "/register",
        data={
            "name": "User B",
            "email": "userb@gmail.com",
            "password": "Password123",
        },
    )

    user_b = User.query.filter_by(
        email="userb@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user_b.id)

    response = client.get("/transactions")

    assert response.status_code == 200
    assert b"UserA_Private_Transaction" not in response.data


def test_user_b_sees_only_own_budgets(client):
    client.post(
        "/register",
        data={
            "name": "User A",
            "email": "usera@gmail.com",
            "password": "Password123",
        },
    )

    user_a = User.query.filter_by(
        email="usera@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user_a.id)

    client.post(
        "/budgets",
        data={
            "category": "UserA_Private_Budget",
            "month": "9",
            "year": "2026",
            "amount": "500",
        },
    )

    client.get("/logout")

    client.post(
        "/register",
        data={
            "name": "User B",
            "email": "userb@gmail.com",
            "password": "Password123",
        },
    )

    user_b = User.query.filter_by(
        email="userb@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user_b.id)

    response = client.get("/budgets")

    assert response.status_code == 200
    assert b"UserA_Private_Budget" not in response.data


def test_user_b_dashboard_does_not_show_user_a_data(client):
    client.post(
        "/register",
        data={
            "name": "User A",
            "email": "usera@gmail.com",
            "password": "Password123",
        },
    )

    user_a = User.query.filter_by(
        email="usera@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user_a.id)

    client.post(
        "/transactions",
        data={
            "type": "expense",
            "amount": "9999",
            "category": "UserA_Private_Category",
            "description": "UserA_Private_Transaction",
            "date": "2026-09-06",
        },
    )

    client.get("/logout")

    client.post(
        "/register",
        data={
            "name": "User B",
            "email": "userb@gmail.com",
            "password": "Password123",
        },
    )

    user_b = User.query.filter_by(
        email="userb@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user_b.id)

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"9999" not in response.data
    assert b"UserA_Private_Transaction" not in response.data


def test_dashboard_calculations(client):
    client.post(
        "/register",
        data={
            "name": "Calculation User",
            "email": "calc@gmail.com",
            "password": "Password123",
        },
    )

    user = User.query.filter_by(
        email="calc@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)

    client.post(
        "/transactions",
        data={
            "type": "income",
            "amount": "1000",
            "category": "Salary",
            "description": "Monthly salary",
            "date": "2026-09-06",
        },
    )

    client.post(
        "/transactions",
        data={
            "type": "expense",
            "amount": "250",
            "category": "Food",
            "description": "Groceries",
            "date": "2026-09-06",
        },
    )

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"750" in response.data


def test_dashboard_savings_rate(client):
    client.post(
        "/register",
        data={
            "name": "Savings User",
            "email": "savings@gmail.com",
            "password": "Password123",
        },
    )

    user = User.query.filter_by(
        email="savings@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)

    client.post(
        "/transactions",
        data={
            "type": "income",
            "amount": "1000",
            "category": "Salary",
            "description": "Monthly salary",
            "date": "2026-09-06",
        },
    )

    client.post(
        "/transactions",
        data={
            "type": "expense",
            "amount": "250",
            "category": "Food",
            "description": "Groceries",
            "date": "2026-09-06",
        },
    )

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"75" in response.data


def test_duplicate_budget_rejected(client):
    client.post(
        "/register",
        data={
            "name": "Budget User",
            "email": "budget@gmail.com",
            "password": "Password123",
        },
    )

    user = User.query.filter_by(
        email="budget@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)

    first_response = client.post(
        "/budgets",
        data={
            "category": "Food",
            "month": "9",
            "year": "2026",
            "amount": "500",
        },
    )

    assert first_response.status_code == 302

    second_response = client.post(
        "/budgets",
        data={
            "category": "Food",
            "month": "9",
            "year": "2026",
            "amount": "700",
        },
    )

    assert second_response.status_code == 400
    assert b"already exists" in second_response.data


def test_invalid_transaction_amount_rejected(client):
    client.post(
        "/register",
        data={
            "name": "Validation User",
            "email": "validation@gmail.com",
            "password": "Password123",
        },
    )

    user = User.query.filter_by(
        email="validation@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)

    response = client.post(
        "/transactions",
        data={
            "type": "expense",
            "amount": "-100",
            "category": "Food",
            "description": "Invalid amount",
            "date": "2026-09-06",
        },
    )

    assert response.status_code == 400
    assert b"greater than 0" in response.data


def test_invalid_transaction_type_rejected(client):
    client.post(
        "/register",
        data={
            "name": "Validation User",
            "email": "type@gmail.com",
            "password": "Password123",
        },
    )

    user = User.query.filter_by(
        email="type@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)

    response = client.post(
        "/transactions",
        data={
            "type": "transfer",
            "amount": "100",
            "category": "Food",
            "description": "Invalid type",
            "date": "2026-09-06",
        },
    )

    assert response.status_code == 400
    assert b"must be income or expense" in response.data


def test_invalid_transaction_date_rejected(client):
    client.post(
        "/register",
        data={
            "name": "Validation User",
            "email": "date@gmail.com",
            "password": "Password123",
        },
    )

    user = User.query.filter_by(
        email="date@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)

    response = client.post(
        "/transactions",
        data={
            "type": "expense",
            "amount": "100",
            "category": "Food",
            "description": "Invalid date",
            "date": "not-a-date",
        },
    )

    assert response.status_code == 400
    assert b"Date must be valid" in response.data


def test_missing_transaction_category_rejected(client):
    client.post(
        "/register",
        data={
            "name": "Validation User",
            "email": "category@gmail.com",
            "password": "Password123",
        },
    )

    user = User.query.filter_by(
        email="category@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)

    response = client.post(
        "/transactions",
        data={
            "type": "expense",
            "amount": "100",
            "category": "",
            "description": "Missing category",
            "date": "2026-09-06",
        },
    )

    assert response.status_code == 400
    assert b"Category is required" in response.data


def test_invalid_budget_amount_rejected(client):
    client.post(
        "/register",
        data={
            "name": "Validation User",
            "email": "budgetamount@gmail.com",
            "password": "Password123",
        },
    )

    user = User.query.filter_by(
        email="budgetamount@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)

    response = client.post(
        "/budgets",
        data={
            "category": "Food",
            "month": "9",
            "year": "2026",
            "amount": "-100",
        },
    )

    assert response.status_code == 400
    assert b"greater than 0" in response.data


def test_invalid_budget_month_rejected(client):
    client.post(
        "/register",
        data={
            "name": "Validation User",
            "email": "month@gmail.com",
            "password": "Password123",
        },
    )

    user = User.query.filter_by(
        email="month@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)

    response = client.post(
        "/budgets",
        data={
            "category": "Food",
            "month": "13",
            "year": "2026",
            "amount": "500",
        },
    )

    assert response.status_code == 400
    assert b"between 1 and 12" in response.data


def test_invalid_budget_year_rejected(client):
    client.post(
        "/register",
        data={
            "name": "Validation User",
            "email": "year@gmail.com",
            "password": "Password123",
        },
    )

    user = User.query.filter_by(
        email="year@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)

    response = client.post(
        "/budgets",
        data={
            "category": "Food",
            "month": "9",
            "year": "2019",
            "amount": "500",
        },
    )

    assert response.status_code == 400
    assert b"2020 or later" in response.data


def test_missing_budget_category_rejected(client):
    client.post(
        "/register",
        data={
            "name": "Validation User",
            "email": "budgetcategory@gmail.com",
            "password": "Password123",
        },
    )

    user = User.query.filter_by(
        email="budgetcategory@gmail.com"
    ).first()

    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)

    response = client.post(
        "/budgets",
        data={
            "category": "",
            "month": "9",
            "year": "2026",
            "amount": "500",
        },
    )

    assert response.status_code == 400
    assert b"Category is required" in response.data


def test_register_rejects_missing_csrf_token(csrf_client):
    response = csrf_client.post(
        "/register",
        data={
            "name": "CSRF Test User",
            "email": "csrf@gmail.com",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 400


def test_transaction_rejects_missing_csrf_token(csrf_client):
    with csrf_client.session_transaction() as session:
        session["_user_id"] = "1"

    response = csrf_client.post(
        "/transactions",
        data={
            "type": "expense",
            "amount": "100",
            "category": "Food",
            "description": "Test",
            "date": "2026-09-06",
        },
    )

    assert response.status_code == 400

def test_budget_rejects_missing_csrf_token(csrf_client):
    with csrf_client.session_transaction() as session:
        session["_user_id"] = "1"

    response = csrf_client.post(
        "/budgets",
        data={
            "category": "Food",
            "month": "9",
            "year": "2026",
            "amount": "2500",
        },
    )

    assert response.status_code == 400


def test_edit_transaction_rejects_missing_csrf_token(csrf_client):
    with csrf_client.session_transaction() as session:
        session["_user_id"] = "1"

    response = csrf_client.post(
        "/transactions/1/edit",
        data={
            "type": "expense",
            "amount": "150",
            "category": "Food",
            "description": "Updated",
            "date": "2026-09-06",
        },
    )

    assert response.status_code == 400

def test_delete_transaction_rejects_missing_csrf_token(csrf_client):
    with csrf_client.session_transaction() as session:
        session["_user_id"] = "1"

    response = csrf_client.post(
        "/transactions/1/delete"
    )

    assert response.status_code == 400


def test_edit_budget_rejects_missing_csrf_token(csrf_client):
    with csrf_client.session_transaction() as session:
        session["_user_id"] = "1"

    response = csrf_client.post(
        "/budgets/1/edit",
        data={
            "category": "Food",
            "month": "9",
            "year": "2026",
            "amount": "2500",
        },
    )

    assert response.status_code == 400


def test_delete_budget_rejects_missing_csrf_token(csrf_client):
    with csrf_client.session_transaction() as session:
        session["_user_id"] = "1"

    response = csrf_client.post(
        "/budgets/1/delete"
    )

    assert response.status_code == 400


def test_custom_500_error_page(client):
    client.application.config["PROPAGATE_EXCEPTIONS"] = False

    with client.application.test_request_context("/"):
        response = client.application.handle_exception(
            Exception("test error")
        )

    assert response.status_code == 500
    assert b"Something Went Wrong" in response.get_data()

    client.application.config["PROPAGATE_EXCEPTIONS"] = None