"""Redis & python-rq related tests"""

import pytest


@pytest.mark.smoke
def test_redis_smoke_test(rq):
    default_queue = rq.get_queue("default")
    default_queue.get_jobs()
    assert True


def add(x, y):
    return x + y


@pytest.mark.smoke
def test_async_task_called_like_regular_function(app, rq):
    rq.job(add)
    assert add(5, 2) == 7


@pytest.mark.smoke
def test_run_regular_function_via_rq(app, rq):
    rq.job(add)
    job = add.queue(5, 2)
    assert job.result == 7


def exception_function():
    raise ValueError


@pytest.mark.smoke
def test_run_exception_function_via_rq(app, rq):
    rq.job(exception_function)

    with pytest.raises(ValueError):
        exception_function.queue()


async def add_coroutine(x, y):
    return x + y


@pytest.mark.smoke
def test_run_coroutine_via_rq(app, rq):
    rq.job(add_coroutine)
    job = add_coroutine.queue(5, 2)
    assert job.result == 7
