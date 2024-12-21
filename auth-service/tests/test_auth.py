"""
Tests for authentication routes
"""

import json
import unittest
from app import create_app, db
# from app.models import User


class TestAuthRoutes(unittest.TestCase):
    """Test cases for authentication routes"""

    def setUp(self):
        """Set up test environment"""
        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
                "JWT_SECRET_KEY": "test-secret-key",
            }
        )
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.test_user_data = {
            "username": "testuser",
            "password": "testpass",
            "email": "test@example.com",
        }

    def tearDown(self):
        """Clean up test environment"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def register_user(self, user_data=None):
        """Helper method to register a user"""
        if user_data is None:
            user_data = self.test_user_data
        return self.client.post("/api/auth/register", json=user_data)

    def login_user(self, credentials=None):
        """Helper method to login a user"""
        if credentials is None:
            credentials = {
                "username": self.test_user_data["username"],
                "password": self.test_user_data["password"],
            }
        return self.client.post("/api/auth/login", json=credentials)

    def test_register_success(self):
        """Test successful user registration"""
        response = self.register_user()
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)
        self.assertIn("user", data)
        self.assertEqual(data["user"]["username"], self.test_user_data["username"])
        self.assertEqual(data["user"]["email"], self.test_user_data["email"])

    def test_register_missing_fields(self):
        """Test registration with missing fields"""
        incomplete_data = {"username": "testuser"}
        response = self.register_user(incomplete_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "Missing required fields")

    def test_register_duplicate_username(self):
        """Test registration with duplicate username"""
        # Register first user
        self.register_user()

        # Try to register with same username
        response = self.register_user()
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 409)
        self.assertEqual(data["error"], "Username already exists")

    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        # Register first user
        self.register_user()

        # Try to register with same email
        duplicate_email_data = {
            "username": "different_user",
            "password": "testpass",
            "email": self.test_user_data["email"],
        }
        response = self.register_user(duplicate_email_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 409)
        self.assertEqual(data["error"], "Email already exists")

    def test_login_success(self):
        """Test successful login"""
        # Register user first
        self.register_user()

        # Try to login
        response = self.login_user()
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)
        self.assertIn("user", data)
        self.assertEqual(data["user"]["username"], self.test_user_data["username"])

    def test_login_missing_fields(self):
        """Test login with missing fields"""
        response = self.login_user({"username": "testuser"})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "Missing username or password")

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        # Register user first
        self.register_user()

        # Try to login with wrong password
        response = self.login_user(
            {"username": self.test_user_data["username"], "password": "wrongpass"}
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["error"], "Invalid username or password")

    def test_refresh_token_success(self):
        """Test successful token refresh"""
        # Register and login to get tokens
        self.register_user()
        login_response = self.login_user()
        login_data = json.loads(login_response.data)
        refresh_token = login_data["refresh_token"]

        # Try to refresh token
        response = self.client.post(
            "/api/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"}
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", data)

    def test_refresh_token_invalid(self):
        """Test refresh with invalid token"""
        response = self.client.post(
            "/api/auth/refresh", headers={"Authorization": "Bearer invalid_token"}
        )

        self.assertEqual(response.status_code, 422)

    def test_verify_success(self):
        """Test successful token verification"""
        # Register and login to get tokens
        self.register_user()
        login_response = self.login_user()
        login_data = json.loads(login_response.data)
        access_token = login_data["access_token"]

        # Try to verify token
        response = self.client.get(
            "/api/auth/verify", headers={"Authorization": f"Bearer {access_token}"}
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("user", data)
        self.assertEqual(data["user"]["username"], self.test_user_data["username"])

    def test_verify_invalid_token(self):
        """Test verify with invalid token"""
        response = self.client.get(
            "/api/auth/verify", headers={"Authorization": "Bearer invalid_token"}
        )

        self.assertEqual(response.status_code, 422)

    def test_verify_missing_token(self):
        """Test verify without token"""
        response = self.client.get("/api/auth/verify")

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
