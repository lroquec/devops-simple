"""
Tests for authentication routes
"""

import json
import unittest
from app import create_app, db
from app.models import User


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
            "role": "user",
        }

        self.test_admin_data = {
            "username": "testadmin",
            "password": "adminpass",
            "email": "admin@example.com",
            "role": "admin",
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

    def register_and_login(self, is_admin=False):
        """Helper method to register and login a user"""
        user_data = self.test_admin_data if is_admin else self.test_user_data
        self.register_user(user_data)
        credentials = {
            "username": user_data["username"],
            "password": user_data["password"],
        }
        response = self.login_user(credentials)
        return json.loads(response.data)

    def test_register_user(self):
        """Test regular user registration"""
        response = self.register_user()
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)
        self.assertIn("user", data)
        self.assertEqual(data["user"]["username"], self.test_user_data["username"])
        self.assertEqual(data["user"]["role"], "user")

    def test_register_admin(self):
        """Test admin user registration"""
        response = self.register_user(self.test_admin_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["user"]["role"], "admin")

    def test_register_duplicate_username(self):
        """Test registration with duplicate username"""
        self.register_user()
        response = self.register_user()
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 409)
        self.assertEqual(data["error"], "Username already exists")

    def test_login_success(self):
        """Test successful login"""
        self.register_user()
        response = self.login_user()
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)
        self.assertEqual(data["user"]["role"], "user")

    def test_login_admin_success(self):
        """Test successful admin login"""
        self.register_user(self.test_admin_data)
        response = self.login_user(
            {
                "username": self.test_admin_data["username"],
                "password": self.test_admin_data["password"],
            }
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["user"]["role"], "admin")

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        self.register_user()
        response = self.login_user(
            {"username": self.test_user_data["username"], "password": "wrongpass"}
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["error"], "Invalid username or password")

    def test_protected_route(self):
        """Test protected route access"""
        data = self.register_and_login()
        token = data["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/api/auth/verify", headers=headers)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("user", data)
        self.assertEqual(data["user"]["role"], "user")

    def test_admin_protected_route(self):
        """Test admin protected route access"""
        data = self.register_and_login(is_admin=True)
        token = data["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/api/auth/verify", headers=headers)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["user"]["role"], "admin")

    def test_refresh_token(self):
        """Test refresh token functionality"""
        data = self.register_and_login()
        refresh_token = data["refresh_token"]

        headers = {"Authorization": f"Bearer {refresh_token}"}
        response = self.client.post("/api/auth/refresh", headers=headers)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("access_token", data)

    def test_invalid_token(self):
        """Test invalid token handling"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = self.client.get("/api/auth/verify", headers=headers)

        self.assertEqual(response.status_code, 422)

    def test_missing_token(self):
        """Test missing token handling"""
        response = self.client.get("/api/auth/verify")
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
