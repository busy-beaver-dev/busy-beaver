from flask import Flask, request

from .config import DATABASE_URI, REDIS_URI
from .extensions import db, migrate, rq
from .exceptions import NotAuthorized
from .toolbox import make_response
from .blueprints import healthcheck_bp, integration_bp, tasks_bp


def handle_http_error(error):
    data = {"message": error.message}
    return make_response(error.status_code, error=data)


def create_app(*, testing=False):
    app = Flask(__name__)

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
    app.config["RQ_QUEUES"] = ["default", "failed"]
    rq.init_app(app)

    app.register_error_handler(NotAuthorized, handle_http_error)

    app.register_blueprint(healthcheck_bp)
    app.register_blueprint(integration_bp)
    app.register_blueprint(tasks_bp)

    @app.before_request
    def add_internal_dictionary():
        """Keep request specific data in `_internal` dictionary"""
        if not getattr(request, "_internal", None):
            request._internal = {}

    return app
