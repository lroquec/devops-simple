import unittest
from unittest.mock import patch, MagicMock
from main import app
from flask import session
import hashlib


class FlaskLoginTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["SECRET_KEY"] = "test_secret_key"
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()

        # Parchar la clase MySQL de flask_mysqldb
        self.mysql_patcher = patch("flask_mysqldb.MySQL", autospec=True)
        self.mock_mysql_class = self.mysql_patcher.start()
        self.mock_mysql = self.mock_mysql_class.return_value

        # Parchar MySQLdb.connect
        self.connect_patcher = patch("MySQLdb.connect", autospec=True)
        self.mock_connect = self.connect_patcher.start()

        # Crear mocks de conexión y cursor
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()

        # Hacer que el mock de connect devuelva la conexión mockeada
        self.mock_connect.return_value = self.mock_connection
        self.mock_connection.cursor.return_value = self.mock_cursor

    def tearDown(self):
        self.mysql_patcher.stop()
        self.connect_patcher.stop()
        self.ctx.pop()

    def configure_mock_cursor(self, fetchone_return=None, fetchall_return=None):
        """Helper para configurar los valores de retorno del cursor mock."""
        self.mock_cursor.fetchone.return_value = fetchone_return
        self.mock_cursor.fetchall.return_value = fetchall_return

    def test_index_redirect(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_login_get(self):
        response = self.app.get("/login/")
        self.assertEqual(response.status_code, 200)

    def test_login_post_success(self):
        hashed_password = hashlib.sha1("testpass".encode()).hexdigest()

        self.configure_mock_cursor(
            fetchone_return={
                "id": 1,
                "username": "testuser",
                "password": hashed_password,
                "role": "user",
            }
        )

        response = self.app.post(
            "/login/",
            data={"username": "testuser", "password": "testpass"},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        with self.app as c:
            with c.session_transaction() as sess:
                self.assertEqual(sess["role"], "user")

    def test_login_post_fail(self):
        self.configure_mock_cursor(fetchone_return=None)

        response = self.app.post(
            "/login/", data={"username": "testuser", "password": "wrongpass"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Incorrect username/password!", response.data)

    def test_logout(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess["loggedin"] = True
                sess["id"] = 1
                sess["username"] = "testuser"

            response = c.get("/login/logout", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertNotIn("loggedin", session)

    def test_register_get(self):
        response = self.app.get("/login/register")
        self.assertEqual(response.status_code, 200)

    def test_register_post_success(self):
        hashed_password = hashlib.sha1("newpass".encode()).hexdigest()

        self.configure_mock_cursor(fetchone_return=None)

        response = self.app.post(
            "/login/register",
            data={
                "username": "newuser",
                "password": "newpass",
                "email": "test@test.com",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"You have successfully registered!", response.data)

        self.mock_cursor.execute.assert_called_with(
            "INSERT INTO accounts (username, password, email, role) VALUES (%s, %s, %s, %s)",
            ("newuser", hashed_password, "test@test.com", "user"),
        )

    def test_register_post_existing_account(self):
        self.configure_mock_cursor(
            fetchone_return={"id": 1, "username": "existinguser"}
        )

        response = self.app.post(
            "/login/register",
            data={
                "username": "existinguser",
                "password": "pass",
                "email": "test@test.com",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Account already exists!", response.data)

    def test_register_invalid_email(self):
        self.configure_mock_cursor(fetchone_return=None)

        response = self.app.post(
            "/login/register",
            data={
                "username": "testuser",
                "password": "testpass",
                "email": "invalid-email",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid email address!", response.data)

    def test_register_invalid_username(self):
        self.configure_mock_cursor(fetchone_return=None)

        response = self.app.post(
            "/login/register",
            data={
                "username": "@testuser",
                "password": "testpass",
                "email": "test@test.com",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"Username must contain only characters and numbers!", response.data
        )

    def test_home_with_session(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess["loggedin"] = True
                sess["username"] = "testuser"

            response = c.get("/login/home")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"testuser", response.data)

    def test_home_without_session(self):
        response = self.app.get("/login/home")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_profile_with_session(self):
        self.configure_mock_cursor(
            fetchone_return={"id": 1, "username": "testuser", "email": "test@test.com"}
        )

        with self.app as c:
            with c.session_transaction() as sess:
                sess["loggedin"] = True
                sess["id"] = 1
                sess["username"] = "testuser"

            response = c.get("/login/profile")
            self.assertEqual(response.status_code, 200)

    def test_profile_without_session(self):
        response = self.app.get("/login/profile")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)


if __name__ == "__main__":
    unittest.main()


# import unittest
# from unittest.mock import patch, MagicMock
# from main import app
# from flask import session
# import os
# import hashlib


# class FlaskLoginTests(unittest.TestCase):
#     def setUp(self):
#         app.config["TESTING"] = True
#         app.config["WTF_CSRF_ENABLED"] = False
#         app.config["SECRET_KEY"] = "test_secret_key"
#         self.app = app.test_client()
#         self.ctx = app.app_context()
#         self.ctx.push()

#         # Parchar la clase MySQL de flask_mysqldb
#         self.mysql_patcher = patch("flask_mysqldb.MySQL", autospec=True)
#         self.mock_mysql_class = self.mysql_patcher.start()
#         self.mock_mysql = self.mock_mysql_class.return_value

#         # Parchar MySQLdb.connect
#         self.connect_patcher = patch("MySQLdb.connect", autospec=True)
#         self.mock_connect = self.connect_patcher.start()

#         # Crear mocks de conexión y cursor
#         self.mock_connection = MagicMock()
#         self.mock_cursor = MagicMock()

#         # Hacer que el mock de connect devuelva la conexión mockeada
#         self.mock_connect.return_value = self.mock_connection
#         self.mock_connection.cursor.return_value = self.mock_cursor

#     def tearDown(self):
#         self.mysql_patcher.stop()
#         self.connect_patcher.stop()
#         self.ctx.pop()

#     def configure_mock_cursor(self, fetchone_return=None, fetchall_return=None):
#         """Helper para configurar los valores de retorno del cursor mock."""
#         self.mock_cursor.fetchone.return_value = fetchone_return
#         self.mock_cursor.fetchall.return_value = fetchall_return

#     def test_index_redirect(self):
#         response = self.app.get("/")
#         self.assertEqual(response.status_code, 302)
#         self.assertIn("/login", response.location)

#     def test_login_get(self):
#         response = self.app.get("/login/")
#         self.assertEqual(response.status_code, 200)

#     def test_login_post_success(self):
#         self.configure_mock_cursor(
#             fetchone_return={
#                 "id": 1,
#                 "username": "testuser",
#                 "password": "hashedpassword",
#             }
#         )

#         response = self.app.post(
#             "/login/",
#             data={"username": "testuser", "password": "testpass"},
#             follow_redirects=True,
#         )

#         self.assertEqual(response.status_code, 200)

#     def test_login_post_fail(self):
#         self.configure_mock_cursor(fetchone_return=None)

#         response = self.app.post(
#             "/login/", data={"username": "testuser", "password": "wrongpass"}
#         )

#         self.assertEqual(response.status_code, 200)
#         self.assertIn(b"Incorrect username/password!", response.data)

#     def test_logout(self):
#         with self.app as c:
#             with c.session_transaction() as sess:
#                 sess["loggedin"] = True
#                 sess["id"] = 1
#                 sess["username"] = "testuser"

#             response = c.get("/login/logout", follow_redirects=True)
#             self.assertEqual(response.status_code, 200)
#             self.assertNotIn("loggedin", session)

#     def test_register_get(self):
#         response = self.app.get("/login/register")
#         self.assertEqual(response.status_code, 200)

#     def test_register_post_success(self):
#         self.configure_mock_cursor(fetchone_return=None)

#         response = self.app.post(
#             "/login/register",
#             data={
#                 "username": "newuser",
#                 "password": "newpass",
#                 "email": "test@test.com",
#             },
#         )

#         self.assertEqual(response.status_code, 200)
#         self.assertIn(b"You have successfully registered!", response.data)

#     def test_register_post_existing_account(self):
#         self.configure_mock_cursor(
#             fetchone_return={"id": 1, "username": "existinguser"}
#         )

#         response = self.app.post(
#             "/login/register",
#             data={
#                 "username": "existinguser",
#                 "password": "pass",
#                 "email": "test@test.com",
#             },
#         )

#         self.assertEqual(response.status_code, 200)
#         self.assertIn(b"Account already exists!", response.data)

#     def test_register_invalid_email(self):
#         # Aseguramos que no exista el usuario (para no mostrar "Account already exists!")
#         self.configure_mock_cursor(fetchone_return=None)

#         response = self.app.post(
#             "/login/register",
#             data={
#                 "username": "testuser",
#                 "password": "testpass",
#                 "email": "invalid-email",
#             },
#         )

#         self.assertEqual(response.status_code, 200)
#         self.assertIn(b"Invalid email address!", response.data)

#     def test_register_invalid_username(self):
#         # Aseguramos que no exista el usuario (para que se valide el username)
#         self.configure_mock_cursor(fetchone_return=None)

#         # Comienza con '@', que no es alfanumérico, esto disparará el mensaje esperado
#         response = self.app.post(
#             "/login/register",
#             data={
#                 "username": "@testuser",
#                 "password": "testpass",
#                 "email": "test@test.com",
#             },
#         )

#         self.assertEqual(response.status_code, 200)
#         self.assertIn(
#             b"Username must contain only characters and numbers!", response.data
#         )

#     def test_home_with_session(self):
#         with self.app as c:
#             with c.session_transaction() as sess:
#                 sess["loggedin"] = True
#                 sess["username"] = "testuser"

#             response = c.get("/login/home")
#             self.assertEqual(response.status_code, 200)
#             self.assertIn(b"testuser", response.data)

#     def test_home_without_session(self):
#         response = self.app.get("/login/home")
#         self.assertEqual(response.status_code, 302)
#         self.assertIn("/login", response.location)

#     def test_profile_with_session(self):
#         self.configure_mock_cursor(
#             fetchone_return={"id": 1, "username": "testuser", "email": "test@test.com"}
#         )

#         with self.app as c:
#             with c.session_transaction() as sess:
#                 sess["loggedin"] = True
#                 sess["id"] = 1
#                 sess["username"] = "testuser"

#             response = c.get("/login/profile")
#             self.assertEqual(response.status_code, 200)

#     def test_profile_without_session(self):
#         response = self.app.get("/login/profile")
#         self.assertEqual(response.status_code, 302)
#         self.assertIn("/login", response.location)

#     @patch.dict("os.environ", {}, clear=True)
#     def test_missing_env_variables(self):
#         with self.assertRaises(KeyError):
#             app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

#     def test_password_hashing(self):
#         with self.app as c:
#             # Simular un input de usuario
#             password = "testpass"
#             secret_key = app.config["SECRET_KEY"]

#             # Calcular el hash esperado
#             hash_input = password + secret_key
#             expected_hashed_password = hashlib.sha1(hash_input.encode()).hexdigest()

#             # Configurar el mock del cursor para devolver un usuario con el hash esperado
#             self.mock_cursor.fetchone.return_value = {
#                 "id": 1,
#                 "username": "testuser",
#                 "password": expected_hashed_password,
#             }

#             # Simular un POST al login con datos correctos
#             response = c.post(
#                 "/login/",
#                 data={"username": "testuser", "password": password},
#                 follow_redirects=True,
#             )

#             # Asegurarse de que la autenticación fue exitosa
#             self.assertEqual(response.status_code, 200)
#             self.assertIn(b"Welcome back, testuser!", response.data)

#     def test_register_hashing(self):
#         with self.app as c:
#             # Simular input del formulario
#             password = "testpass"
#             email = "testuser@example.com"
#             username = "testuser"

#             # Calcular el hash esperado
#             secret_key = app.config["SECRET_KEY"]
#             hash_input = password + secret_key
#             expected_hashed_password = hashlib.sha1(hash_input.encode()).hexdigest()

#             # Configurar el mock del cursor para simulación
#             self.mock_cursor.fetchone.return_value = None  # Usuario no existente
#             self.mock_cursor.execute.return_value = None

#             # Simular POST al registro
#             response = c.post(
#                 "/login/register",
#                 data={"username": username, "password": password, "email": email},
#                 follow_redirects=True,
#             )

#             # Validar que el hash se generó y fue usado
#             self.assertEqual(response.status_code, 200)
#             self.mock_cursor.execute.assert_called_with(
#                 "INSERT INTO accounts VALUES (NULL, %s, %s, %s)",
#                 (username, expected_hashed_password, email),
#             )
#             self.assertIn(b"You have successfully registered!", response.data)


# if __name__ == "__main__":
#     unittest.main()
