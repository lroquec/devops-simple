import unittest
from flask import json
from app import create_app, db
from app.models import User, RevokedToken
import os


class AuthTests(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        os.environ["SECRET_KEY"] = "test-secret-key"
        os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key"

        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_success(self):
        """Test successful user registration"""
        response = self.client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "testpass",
                "email": "test@test.com",
            },
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "User registered successfully")

    def test_register_duplicate_username(self):
        """Test registration with existing username"""
        # Create first user
        self.client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "testpass",
                "email": "test@test.com",
            },
        )

        # Try to create duplicate
        response = self.client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "testpass2",
                "email": "test2@test.com",
            },
        )
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Username already exists")

    def test_login_success(self):
        """Test successful login"""
        # Register user
        self.client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "testpass",
                "email": "test@test.com",
            },
        )

        # Login
        response = self.client.post(
            "/api/auth/login", json={"username": "testuser", "password": "testpass"}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)
        self.assertIn("user", data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(
            "/api/auth/login", json={"username": "wronguser", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Invalid username or password")

    def test_verify_token(self):
        """Test token verification"""
        # Register and login user
        self.client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "testpass",
                "email": "test@test.com",
            },
        )

        login_response = self.client.post(
            "/api/auth/login", json={"username": "testuser", "password": "testpass"}
        )
        token = json.loads(login_response.data)["access_token"]

        # Verify token
        response = self.client.get(
            "/api/auth/verify", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["username"], "testuser")

    def test_logout(self):
        """Test logout functionality"""
        # Register and login user
        self.client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "testpass",
                "email": "test@test.com",
            },
        )

        login_response = self.client.post(
            "/api/auth/login", json={"username": "testuser", "password": "testpass"}
        )
        token = json.loads(login_response.data)["access_token"]

        # Logout
        response = self.client.post(
            "/api/auth/logout", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Successfully logged out")

    def test_password_hashing(self):
        """Test password hashing functionality"""
        with self.app.app_context():
            user = User(
                username="testuser",
                email="test@test.com",
                password=User.hash_password("testpass"),
            )
            db.session.add(user)
            db.session.commit()

            self.assertTrue(user.verify_password("testpass"))
            self.assertFalse(user.verify_password("wrongpass"))


if __name__ == "__main__":
    unittest.main()
