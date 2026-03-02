from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "login"


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = "change-this-secret-in-production"

    instance_dir = Path(app.instance_path)
    instance_dir.mkdir(parents=True, exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{instance_dir / 'finance.db'}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    from . import routes

    routes.init_routes(app)

    with app.app_context():
        db.create_all()

    return app
