from flask_login import LoginManager
from flask_migrate import Migrate
from flask_rq2 import RQ
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
rq = RQ()
talisman = Talisman()
