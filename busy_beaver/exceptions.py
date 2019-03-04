class BusyBeaverException(Exception):
    pass


class UnexpectedStatusCode(BusyBeaverException):
    pass


class NotFoundError(BusyBeaverException):
    status_code = 404

    def __init__(self, object_type):
        super().__init__()
        self.message = f"{object_type} not found"

        return self.payload.copy()
