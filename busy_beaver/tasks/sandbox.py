from busy_beaver.extensions import rq


@rq.job
def add(x, y):
    return x + y
