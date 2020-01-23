import functools
from typing import List

from .toolbox import make_slack_response


def limit_to(workspace_ids: List[str]):
    """This decorator limits functionality to specified workspace_ids"""

    if not isinstance(workspace_ids, list):
        raise ValueError

    def limit_to_decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            team_id = kwargs["team_id"]
            if team_id not in workspace_ids:
                return make_slack_response(text="Command not supported at this time.")

            return func(*args, **kwargs)

        return _wrapper

    return limit_to_decorator
