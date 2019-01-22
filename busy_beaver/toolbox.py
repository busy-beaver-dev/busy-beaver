from datetime import datetime, timedelta

import pytz


def utc_now_minus(period: timedelta):
    return pytz.utc.localize(datetime.utcnow()) - period
