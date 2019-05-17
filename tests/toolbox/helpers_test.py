from datetime import datetime, timedelta
import pytest
from busy_beaver.toolbox import utc_now_minus


@pytest.mark.freeze_time("2019-05-12")
def test_utc_now_minus():
    today = datetime.utcnow()

    result = utc_now_minus(timedelta(days=1))

    assert result.replace(tzinfo=None) == today - timedelta(days=1)
