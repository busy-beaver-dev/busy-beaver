class BusyBeaverException(Exception):
    pass


class UnexpectedStatusCode(BusyBeaverException):
    pass


class NotFoundError(BusyBeaverException):
    status_code = 404

    def __init__(self, object_type):
        super().__init__()
        self.message = f"{object_type} not found"


class DeserializationError(BusyBeaverException):
    status_code = 422

    def __init__(self, payload):
        super().__init__()
        self.message = "Marshmallow Deserialization Error"
        self.payload = payload

    def to_dict(self):
        return self.payload.copy()


class SerializationError(BusyBeaverException):
    status_code = 500

    def __init__(self, payload):
        super().__init__()
        self.message = "Marshmallow Serialization Error"
        self.payload = payload

    def to_dict(self):
        return self.payload.copy()
