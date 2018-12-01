from sqlalchemy_wrapper import SQLAlchemy

from .config import DATABASE_URI


db = SQLAlchemy(DATABASE_URI)
from . import models  # noqa

from .server import api

if __name__ == "__main__":
    api.run(address="0.0.0.0", port=5100, debug=True)
