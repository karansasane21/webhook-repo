from flask import Flask
from app.extensions import db
from app.webhook.routes import webhook

def create_app():
    app = Flask(__name__)

    # Database configuration (using SQLite for demo)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///webhook.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Init DB
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(webhook)

    # Create tables
    with app.app_context():
        from app.models import WebhookEvent
        db.create_all()

    return app