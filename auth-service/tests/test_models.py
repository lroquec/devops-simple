"""
Tests for database models
"""

import unittest
from datetime import datetime
from app import create_app, db
from app.models import User


class TestModels(unittest.TestCase):
    """Test cases for database models"""

    def setUp(self):
        """Set up test environment"""
        self.app = create_app(
            {"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"}
        )
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clean up test environment"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_creation(self):
        """Test user model creation"""
        user = User(
            username="test_user",
            password="test_password",
            email="test@example.com",
            role="user",
        )
        db.session.add(user)
        db.session.commit()

        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, "test_user")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.role, "user")
        self.assertIsInstance(user.created_at, datetime)
        self.assertIsInstance(user.updated_at, datetime)

    def test_admin_user_creation(self):
        """Test admin user model creation"""
        admin = User(
            username="admin_user",
            password="admin_password",
            email="admin@example.com",
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()

        self.assertEqual(admin.role, "admin")
        self.assertIsNotNone(admin.id)

    def test_default_role(self):
        """Test default role assignment"""
        user = User(
            username="default_user",
            password="test_password",
            email="default@example.com",
        )
        db.session.add(user)
        db.session.commit()

        self.assertEqual(user.role, "user")  # Should default to 'user'

    def test_user_to_dict(self):
        """Test user model to_dict method"""
        user = User(
            username="test_user",
            password="test_password",
            email="test@example.com",
            role="user",
        )
        db.session.add(user)
        db.session.commit()

        user_dict = user.to_dict()
        self.assertIsInstance(user_dict, dict)
        self.assertEqual(user_dict["username"], "test_user")
        self.assertEqual(user_dict["email"], "test@example.com")
        self.assertEqual(user_dict["role"], "user")
        self.assertIsNotNone(user_dict["created_at"])
        self.assertIsNotNone(user_dict["updated_at"])

    def test_invalid_role(self):
        """Test that invalid roles raise an error"""
        with self.assertRaises(Exception):
            user = User(
                username="invalid_role_user",
                password="test_password",
                email="invalid@example.com",
                role="invalid_role",  # This should raise an error
            )
            db.session.add(user)
            db.session.commit()

    def test_user_unique_constraints(self):
        """Test user model unique constraints"""
        user1 = User(
            username="test_user",
            password="test_password",
            email="test@example.com",
            role="user",
        )
        db.session.add(user1)
        db.session.commit()

        user2 = User(
            username="test_user",  # Same username
            password="test_password",
            email="different@example.com",
            role="user",
        )

        with self.assertRaises(Exception):
            db.session.add(user2)
            db.session.commit()

        db.session.rollback()

        user3 = User(
            username="different_user",
            password="test_password",
            email="test@example.com",  # Same email
            role="user",
        )

        with self.assertRaises(Exception):
            db.session.add(user3)
            db.session.commit()


if __name__ == "__main__":
    unittest.main()
