from sqlalchemy_wrapper import SQLAlchemy

from .config import DATABASE_URI


db = SQLAlchemy(DATABASE_URI)
from . import models  # noqa
