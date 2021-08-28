from busy_beaver.extensions import rq


@rq.job
def add(x, y):
    return x + y


@rq.job
async def add_async(x, y):
    return x + y


"""
# How to debug

make flaskshell

from datetime import timedelta
from busy_beaver.apps.debug.workflows import add, add_async


job = add.queue(3, 4)
job.result

job = add_async.schedule(timedelta(seconds=5), 1, 2)
job.result

job = add.queue(3, 4)
job.result

job = add_async.schedule(timedelta(seconds=5), 1, 2)
job.result
"""
# app.config['RQ_SCHEDULER_QUEUE'] = 'scheduled'
# app.config['RQ_SCHEDULER_INTERVAL'] = 1 default is 60
