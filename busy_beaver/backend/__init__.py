from .. import api
from .github import GitHubIdentityVerificationCallbackResource
from .sandbox import HelloWorldResource, GoodbyeWorldResource
from .slack import SlackEventSubscriptionResource
from .tasks import PublishGitHubSummaryResource, TwitterPollingResource

api.add_route("/hello", HelloWorldResource())
api.add_route("/goodbye", GoodbyeWorldResource())

api.add_route("/github-integration", GitHubIdentityVerificationCallbackResource())
api.add_route("/slack-event-subscription", SlackEventSubscriptionResource())

api.add_route("/github-summary", PublishGitHubSummaryResource())
api.add_route("/poll-twitter", TwitterPollingResource())
