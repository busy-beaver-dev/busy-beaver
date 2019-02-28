from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from ..config import SQLALCHEMY_DATABASE_URI
from .exceptions import NotFoundError, DeserializationError, SerializationError
from .utilities import make_response
from .blueprints import healthcheck_bp, cron_bp

db = SQLAlchemy()
migrate = Migrate()
from .models import *  # noqa


def handle_not_found_error(error):
    data = {"msg": error.message}
    return make_response(error.status_code, error=data)


def handle_validation_error(error):
    return make_response(error.status_code, error=error.payload)


def create_app(*, testing=False):
    app = Flask(__name__)

    # use environment variables if in prod
    if testing:
        app.config["TESTING"] = True
        database_uri = "sqlite:///:memory:"
    else:
        database_uri = SQLALCHEMY_DATABASE_URI

    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate.init_app(app, db)

    app.register_error_handler(NotFoundError, handle_not_found_error)
    app.register_error_handler(DeserializationError, handle_not_found_error)
    app.register_error_handler(SerializationError, handle_not_found_error)

    app.register_blueprint(cron_bp, url_prefix="/api/v1/")
    app.register_blueprint(healthcheck_bp, url_prefix="/api")

    return app
