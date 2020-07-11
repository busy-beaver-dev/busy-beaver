class BusyBeaverException(Exception):
    pass


class AsyncException(BusyBeaverException):
    pass


class EventEmitterException(BusyBeaverException):
    pass


class EventEmitterEventAlreadyRegistered(EventEmitterException):
    pass


class EventEmitterEventNotRegistered(EventEmitterException):
    pass


class GitHubSummaryException(BusyBeaverException):
    pass


class NoMeetupEventsFound(BusyBeaverException):
    pass


class NotFound(BusyBeaverException):
    status_code = 404

    def __init__(self, object_type):
        super().__init__()
        self.message = f"{object_type} not found"


class NotAuthorized(BusyBeaverException):
    status_code = 401

    def __init__(self, error):
        super().__init__()
        self.message = error


class SlackTooManyBlocks(BusyBeaverException):
    pass


class StateMachineError(BusyBeaverException):
    status_code = 500

    def __init__(self, error):
        super().__init__()
        self.message = error


class UnverifiedWebhookRequest(NotAuthorized):
    pass


class UnexpectedStatusCode(BusyBeaverException):
    pass


class ValidationError(BusyBeaverException):
    status_code = 422

    def __init__(self, error):
        super().__init__()
        self.message = error
