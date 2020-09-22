from busy_beaver.common.models import BaseModel, Task  # noqa isort:skip

from busy_beaver.apps.github_integration.models import (  # noqa
    GitHubSummaryConfiguration,
    GitHubSummaryUser,
)
from busy_beaver.apps.slack_integration.models import (  # noqa
    SlackInstallation,
    SlackUser,
)
from busy_beaver.apps.upcoming_events.models import (  # noqa
    Event,
    UpcomingEventsConfiguration,
    UpcomingEventsGroup,
)
from busy_beaver.apps.youtube_integration.models import YouTubeVideo  # noqa
