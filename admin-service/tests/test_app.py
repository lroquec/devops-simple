import pytest
from unittest.mock import patch, MagicMock
from main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():  # Activa el contexto de la aplicación para los tests
            yield client


@patch("main.mysql.connection.cursor")  # Mock the MySQL cursor
def test_login_success(mock_cursor, client):
    # Mock the database response
    mock_cursor.return_value.__enter__.return_value.fetchone.return_value = {
        "id": 1,
        "username": "test_user",
        "password": "hashed_password",
        "role": "admin",
    }

    # Simulate a login request
    with app.app_context():  # Activa el contexto para este test
        response = client.post(
            "/login",
            data={"username": "test_user", "password": "test_password"},
            follow_redirects=True,
        )

    # Assertions
    assert response.status_code == 200
    assert b"Users List" in response.data


@patch("main.mysql.connection.cursor")
def test_login_failure(mock_cursor, client):
    # Simulate no user found in the database
    mock_cursor.return_value.__enter__.return_value.fetchone.return_value = None

    # Simulate a login request
    with app.app_context():
        response = client.post(
            "/login",
            data={"username": "invalid_user", "password": "wrong_password"},
            follow_redirects=True,
        )

    # Assertions
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


@patch("main.mysql.connection.cursor")
def test_list_users(mock_cursor, client):
    # Mock the database response for users
    mock_cursor.return_value.__enter__.return_value.fetchall.return_value = [
        {"id": 1, "username": "test_user", "email": "test@example.com", "role": "admin"}
    ]

    # Simulate an authenticated session
    with client.session_transaction() as sess:
        sess["loggedin"] = True
        sess["role"] = "admin"

    # Simulate a request to the users page
    with app.app_context():
        response = client.get("/users")

    # Assertions
    assert response.status_code == 200
    assert b"test_user" in response.data
