import unittest
from datetime import datetime
from app import create_app, db
from app.models import User, RevokedToken
import os


class ModelTests(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        os.environ["SECRET_KEY"] = "test-secret-key"
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

    def test_user_creation(self):
        """Test user model creation and attributes"""
        with self.app.app_context():
            user = User(
                username="testuser",
                email="test@test.com",
                password=User.hash_password("testpass"),
                role="user",
            )
            db.session.add(user)
            db.session.commit()

            # Test user attributes
            self.assertEqual(user.username, "testuser")
            self.assertEqual(user.email, "test@test.com")
            self.assertEqual(user.role, "user")
            self.assertIsInstance(user.created_at, datetime)
            self.assertIsInstance(user.updated_at, datetime)

    def test_user_password_hashing(self):
        """Test password hashing and verification"""
        with self.app.app_context():
            password = "testpass"
            user = User(
                username="testuser",
                email="test@test.com",
                password=User.hash_password(password),
            )

            # Test password verification
            self.assertTrue(user.verify_password(password))
            self.assertFalse(user.verify_password("wrongpass"))

    def test_user_to_dict(self):
        """Test user serialization to dictionary"""
        with self.app.app_context():
            user = User(
                username="testuser",
                email="test@test.com",
                password=User.hash_password("testpass"),
                role="user",
            )
            db.session.add(user)
            db.session.commit()

            user_dict = user.to_dict()
            self.assertEqual(user_dict["username"], "testuser")
            self.assertEqual(user_dict["email"], "test@test.com")
            self.assertEqual(user_dict["role"], "user")
            self.assertIsNone(user_dict["avatar_path"])
            self.assertIn("created_at", user_dict)
            self.assertIn("updated_at", user_dict)

    def test_revoked_token(self):
        """Test revoked token model"""
        with self.app.app_context():
            token = RevokedToken(jti="test-token-123")
            db.session.add(token)
            db.session.commit()

            # Test token revocation check
            self.assertTrue(RevokedToken.is_token_revoked("test-token-123"))
            self.assertFalse(RevokedToken.is_token_revoked("non-existent-token"))

    def test_user_unique_constraints(self):
        """Test unique constraints on username and email"""
        with self.app.app_context():
            user1 = User(
                username="testuser",
                email="test@test.com",
                password=User.hash_password("testpass"),
            )
            db.session.add(user1)
            db.session.commit()

            # Try to create user with same username
            user2 = User(
                username="testuser",
                email="different@test.com",
                password=User.hash_password("testpass"),
            )
            db.session.add(user2)
            with self.assertRaises(Exception):
                db.session.commit()
            db.session.rollback()

            # Try to create user with same email
            user3 = User(
                username="differentuser",
                email="test@test.com",
                password=User.hash_password("testpass"),
            )
            db.session.add(user3)
            with self.assertRaises(Exception):
                db.session.commit()


if __name__ == "__main__":
    unittest.main()
