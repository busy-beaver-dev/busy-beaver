from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_rq2 import RQ

db = SQLAlchemy()
migrate = Migrate()
rq = RQ()
