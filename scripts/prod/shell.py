from busy_beaver import create_app
from busy_beaver.extensions import db, rq  # noqa
from busy_beaver.models import *  # noqa

# create flask application context
app = create_app()
ctx = app.app_context()
ctx.push()

# log to console
display_text = "Busy Beaver Production Shell"
num_char = len(display_text)
print("*" * num_char)
print(display_text)
print("*" * num_char)
