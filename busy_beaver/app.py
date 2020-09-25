from flask import Flask, request
from secure import SecureHeaders
from whitenoise import WhiteNoise

from .blueprints import cfps_bp, events_bp, github_bp, healthcheck_bp, slack_bp, web_bp
from .common.oauth import OAuthError
from .config import DATABASE_URI, REDIS_URI, SECRET_KEY
from .exceptions import NotAuthorized, StateMachineError, ValidationError
from .extensions import bootstrap, db, login_manager, migrate, rq
from .toolbox import make_response


def handle_error(error):
    data = {"message": error.message}
    return make_response(error.status_code, error=data)


def create_app(*, testing=False):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY

    if testing:
        app.config["TESTING"] = True
        database_uri = "sqlite:///:memory:"
        app.config["RQ_ASYNC"] = False
        app.config["WTF_CSRF_ENABLED"] = False
    else:
        database_uri = DATABASE_URI

    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate.init_app(app, db)

    app.config["RQ_REDIS_URL"] = REDIS_URI
    app.config["RQ_QUEUES"] = ["default", "failed"]
    rq.init_app(app)

    bootstrap.init_app(app)
    login_manager.init_app(app)

    app.register_error_handler(NotAuthorized, handle_error)
    app.register_error_handler(OAuthError, handle_error)
    app.register_error_handler(ValidationError, handle_error)
    app.register_error_handler(StateMachineError, handle_error)

    app.register_blueprint(cfps_bp, cli_group=None)
    app.register_blueprint(events_bp, cli_group=None)
    app.register_blueprint(healthcheck_bp)
    app.register_blueprint(github_bp, url_prefix="/github", cli_group=None)
    app.register_blueprint(slack_bp, url_prefix="/slack")
    app.register_blueprint(web_bp)

    app.wsgi_app = WhiteNoise(
        app.wsgi_app, root="busy_beaver/static/", prefix="assets/"
    )

    @app.before_request
    def add_internal_dictionary():
        """Keep request specific data in `_internal` dictionary"""
        if not getattr(request, "_internal", None):
            request._internal = {}

    secure_headers = SecureHeaders()

    @app.after_request
    def set_secure_headers(response):
        secure_headers.flask(response)
        return response

    return app
