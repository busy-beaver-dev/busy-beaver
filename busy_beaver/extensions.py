from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_rq2 import RQ
from flask_talisman import Talisman

db = SQLAlchemy()
migrate = Migrate()
rq = RQ()
talisman = Talisman()
