class BusyBeaverException(Exception):
    pass


class AsyncException(BusyBeaverException):
    pass


class NotAuthorized(BusyBeaverException):
    status_code = 401

    def __init__(self, error):
        super().__init__()
        self.message = error


class UnverifiedSlackRequest(NotAuthorized):
    pass


class NotFound(BusyBeaverException):
    status_code = 404

    def __init__(self, object_type):
        super().__init__()
        self.message = f"{object_type} not found"


class UnexpectedStatusCode(BusyBeaverException):
    pass
