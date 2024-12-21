import pytest
from unittest.mock import MagicMock, patch
from main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():  # Activar el contexto para evitar errores
            yield client


# Mock completo de flask_mysqldb.MySQL
@pytest.fixture(autouse=True)
def mock_mysql():
    with patch("main.mysql") as mock_mysql:
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_mysql.connection = mock_connection
        yield mock_cursor  # Permite personalizar el mock dentro de los tests


def test_login_success(mock_mysql, client):
    # Configura el mock para devolver un usuario válido
    mock_mysql.fetchone.return_value = {
        "id": 1,
        "username": "test_user",
        "password": "hashed_password",
        "role": "admin",
    }

    # Simula una solicitud de login válida
    response = client.post(
        "/login",
        data={"username": "test_user", "password": "test_password"},
        follow_redirects=True,
    )

    # Aserciones
    assert response.status_code == 200
    assert b"Users List" in response.data


def test_login_failure(mock_mysql, client):
    # Configura el mock para devolver None (usuario no encontrado)
    mock_mysql.fetchone.return_value = None

    # Simula una solicitud de login inválida
    response = client.post(
        "/login",
        data={"username": "invalid_user", "password": "wrong_password"},
        follow_redirects=True,
    )

    # Aserciones
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_list_users(mock_mysql, client):
    # Configura el mock para devolver una lista de usuarios
    mock_mysql.fetchall.return_value = [
        {"id": 1, "username": "test_user", "email": "test@example.com", "role": "admin"}
    ]

    # Simula una sesión autenticada
    with client.session_transaction() as sess:
        sess["loggedin"] = True
        sess["role"] = "admin"

    # Simula una solicitud a la página de usuarios
    response = client.get("/users")

    # Aserciones
    assert response.status_code == 200
    assert b"test_user" in response.data
