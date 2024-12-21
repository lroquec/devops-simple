"""
Authentication service implementation using Flask factory pattern
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()


def create_app(test_config=None):
    """Create and configure the Flask application

    Args:
        test_config (dict, optional): Test configuration to override defaults. Defaults to None.

    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)

    # Default configuration
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///auth.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "dev-secret-key"),
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=1),
        JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=30),
    )

    # Override config with test config if passed
    if test_config is not None:
        app.config.update(test_config)

    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    from app.routes import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Create database tables
    with app.app_context():
        db.create_all()

    # Register error handlers
    @app.errorhandler(Exception)
    def handle_error(error):
        """Global error handler"""
        app.logger.error(f"Error: {str(error)}")
        return {"error": "Internal server error"}, 500

    return app
