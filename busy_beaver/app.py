from flask import Flask, request

from .blueprints import (
    events_bp,
    github_bp,
    healthcheck_bp,
    poller_bp,
    slack_bp,
    twitter_bp,
)
from .common.oauth import OAuthError
from .config import DATABASE_URI, REDIS_URI, SECRET_KEY
from .exceptions import NotAuthorized, ValidationError
from .extensions import db, migrate, rq, talisman
from .toolbox import make_response


def handle_http_error(error):
    data = {"message": error.message}
    return make_response(error.status_code, error=data)


def handle_oauth_error(error):
    data = {"message": error.message}
    return make_response(error.status_code, error=data)


def handle_validation_error(error):
    data = {"message": error.message}
    return make_response(error.status_code, error=data)


def create_app(*, testing=False):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY

    if testing:
        app.config["TESTING"] = True
        database_uri = "sqlite:///:memory:"
        app.config["RQ_ASYNC"] = False
    else:
        database_uri = DATABASE_URI

    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate.init_app(app, db)

    app.config["RQ_REDIS_URL"] = REDIS_URI
    app.config["RQ_QUEUES"] = ["busybeaver_default"]
    rq.init_app(app)

    talisman.init_app(app)

    app.register_error_handler(NotAuthorized, handle_http_error)
    app.register_error_handler(OAuthError, handle_oauth_error)
    app.register_error_handler(ValidationError, handle_validation_error)

    app.register_blueprint(events_bp, cli_group=None)
    app.register_blueprint(healthcheck_bp)
    app.register_blueprint(github_bp, url_prefix="/github", cli_group=None)
    app.register_blueprint(poller_bp, url_prefix="/poll")
    app.register_blueprint(slack_bp, url_prefix="/slack")
    app.register_blueprint(twitter_bp, cli_group=None)

    @app.before_request
    def add_internal_dictionary():
        """Keep request specific data in `_internal` dictionary"""
        if not getattr(request, "_internal", None):
            request._internal = {}

    return app
