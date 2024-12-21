from app import db
from datetime import datetime
import hashlib
import os

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.Enum('user', 'admin'), nullable=False, default='user')
    avatar_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def hash_password(password):
        """Hash password with app's secret key"""
        hash_input = password + os.getenv('SECRET_KEY', 'dev-key')
        return hashlib.sha1(hash_input.encode()).hexdigest()

    def verify_password(self, password):
        """Verify password against stored hash"""
        return self.password == self.hash_password(password)

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'avatar_path': self.avatar_path,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class RevokedToken(db.Model):
    __tablename__ = 'revoked_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), unique=True, nullable=False)
    revoked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @classmethod
    def is_token_revoked(cls, jti):
        """Check if a token is revoked"""
        return bool(cls.query.filter_by(jti=jti).first())
