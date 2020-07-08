from busy_beaver.app import create_app
from busy_beaver.extensions import rq

app = create_app()
ctx = app.app_context()
ctx.push()

scheduler = rq.get_scheduler(interval=10)
scheduler.run()
