import pytest

from busy_beaver.extensions import rq


@pytest.mark.smoke
def test_redis_smoke_test():
    default_queue = rq.get_queue("default")
    default_queue.get_jobs()

    assert True
