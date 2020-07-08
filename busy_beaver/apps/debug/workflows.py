from busy_beaver.extensions import rq


@rq.job
def add(x, y):
    return x + y


"""
make devshell

from busy_beaver.apps.debug.workflows import add
job = add.queue(3, 4)
job.result
"""
