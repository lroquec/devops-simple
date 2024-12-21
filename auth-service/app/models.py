"""
Database models for the authentication service
"""

from datetime import datetime
from sqlalchemy.exc import StatementError
from app import db

VALID_ROLES = ("user", "admin")


class User(db.Model):
    """User model for authentication"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(
        db.Enum("user", "admin", name="user_roles"), nullable=False, default="user"
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __init__(self, username, password, email, role="user"):
        if role not in VALID_ROLES:
            raise ValueError(f"Invalid role. Must be one of: {VALID_ROLES}")

        self.username = username
        self.password = password
        self.email = email
        self.role = role

    def to_dict(self):
        """Convert user object to dictionary

        Returns:
            dict: User data dictionary
        """
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<User {self.username}>"
