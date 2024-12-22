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
    assert b"Users Management" in response.data


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


def test_add_user(mock_mysql, client):
    # Mock the cursor and database response
    mock_mysql.fetchone.return_value = None  # Simula que no hay usuario duplicado
    mock_mysql.fetchall.return_value = []  # Simula que no hay email duplicado

    # Simula una sesión autenticada
    with client.session_transaction() as sess:
        sess["loggedin"] = True
        sess["role"] = "admin"

    # Simula una solicitud POST para agregar un usuario
    response = client.post(
        "/add_user",
        data={
            "username": "new_user",
            "password": "secure_password",
            "email": "new_user@example.com",
            "role": "user",
        },
        follow_redirects=True,
    )

    # Aserciones
    assert response.status_code == 200
    assert b"Users Management" in response.data  # Redirige a la lista de usuarios


def test_delete_user(mock_mysql, client):
    # Simula una sesión autenticada
    with client.session_transaction() as sess:
        sess["loggedin"] = True
        sess["role"] = "admin"

    # Simula una solicitud POST para eliminar un usuario
    response = client.post("/delete_user/1", follow_redirects=True)

    # Aserciones
    assert response.status_code == 200
    assert b"Users Management" in response.data


def test_protected_route_without_login(client):
    # Intenta acceder a una ruta protegida sin iniciar sesión
    response = client.get("/users", follow_redirects=True)

    # Aserciones
    assert response.status_code == 200
    assert b"Login" in response.data  # Redirige al login


def test_database_error(mock_mysql, client):
    # Configura el mock para lanzar una excepción
    mock_mysql.execute.side_effect = Exception("Database error")

    # Simula una sesión autenticada
    with client.session_transaction() as sess:
        sess["loggedin"] = True
        sess["role"] = "admin"

    # Simula una solicitud a la página de usuarios
    response = client.get("/users")

    # Aserciones
    assert response.status_code == 500
    assert b"An error occurred while fetching users." in response.data


def test_edit_user_get(mock_mysql, client):
    # Configura el mock para devolver un usuario
    mock_mysql.fetchone.return_value = {
        "id": 1,
        "username": "test_user",
        "email": "test@example.com",
        "role": "user",
    }

    # Simula una sesión autenticada
    with client.session_transaction() as sess:
        sess["loggedin"] = True
        sess["role"] = "admin"

    # Simula una solicitud GET para editar un usuario
    response = client.get("/edit_user/1")

    # Aserciones
    assert response.status_code == 200
    assert b"test_user" in response.data


def test_edit_user_post(mock_mysql, client):
    # Mock para verificar usuario duplicado
    mock_mysql.fetchone.side_effect = [None, None]  # No hay duplicados

    # Simula una sesión autenticada
    with client.session_transaction() as sess:
        sess["loggedin"] = True
        sess["role"] = "admin"

    # Simula una solicitud POST para editar un usuario
    response = client.post(
        "/edit_user/1",
        data={
            "username": "updated_user",
            "email": "updated@example.com",
            "role": "user",
            "password": "new_password",
        },
        follow_redirects=True,
    )

    # Aserciones
    assert response.status_code == 200
    assert b"Users Management" in response.data


def test_edit_user_invalid_email(mock_mysql, client):
    # Simula una sesión autenticada
    with client.session_transaction() as sess:
        sess["loggedin"] = True
        sess["role"] = "admin"

    # Simula una solicitud POST con email inválido
    response = client.post(
        "/edit_user/1",
        data={
            "username": "test_user",
            "email": "invalid-email",
            "role": "user",
            "password": "",
        },
    )

    # Aserciones
    assert b"Invalid email format" in response.data


def test_add_user_invalid_email(mock_mysql, client):
    # Simula una sesión autenticada
    with client.session_transaction() as sess:
        sess["loggedin"] = True
        sess["role"] = "admin"

    # Simula una solicitud POST con email inválido
    response = client.post(
        "/add_user",
        data={
            "username": "new_user",
            "password": "password123",
            "email": "invalid-email",
            "role": "user",
        },
    )

    # Aserciones
    assert b"Invalid email format" in response.data


def test_add_user_duplicate_username(mock_mysql, client):
    # Mock para simular usuario duplicado
    mock_mysql.fetchone.return_value = {"username": "existing_user"}

    # Simula una sesión autenticada
    with client.session_transaction() as sess:
        sess["loggedin"] = True
        sess["role"] = "admin"

    # Simula una solicitud POST con username duplicado
    response = client.post(
        "/add_user",
        data={
            "username": "existing_user",
            "password": "password123",
            "email": "new@example.com",
            "role": "user",
        },
    )

    # Aserciones
    assert b"Username already exists" in response.data


def test_add_user_duplicate_email(mock_mysql, client):
    # Mock para simular email duplicado (primer fetchone para username, segundo para email)
    mock_mysql.fetchone.side_effect = [None, {"email": "existing@example.com"}]

    # Simula una sesión autenticada
    with client.session_transaction() as sess:
        sess["loggedin"] = True
        sess["role"] = "admin"

    # Simula una solicitud POST con email duplicado
    response = client.post(
        "/add_user",
        data={
            "username": "new_user",
            "password": "password123",
            "email": "existing@example.com",
            "role": "user",
        },
    )

    # Aserciones
    assert b"Email already exists" in response.data


def test_logout(client):
    # Primero establece una sesión
    with client.session_transaction() as sess:
        sess["loggedin"] = True
        sess["id"] = 1
        sess["username"] = "test_user"
        sess["role"] = "admin"

    # Simula una solicitud de logout
    response = client.get("/logout", follow_redirects=True)

    # Verifica que la sesión esté vacía
    with client.session_transaction() as sess:
        assert "loggedin" not in sess
        assert "id" not in sess
        assert "username" not in sess
        assert "role" not in sess

    # Verifica que redirija al login
    assert response.status_code == 200
    assert b"Login" in response.data
