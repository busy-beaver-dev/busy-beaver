from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_rq2 import RQ
from flask_sqlalchemy import SQLAlchemy

bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()
rq = RQ()

login_manager = LoginManager()
login_manager.login_view = "web.login"
