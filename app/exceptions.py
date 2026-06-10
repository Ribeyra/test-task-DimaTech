class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return self.message


class NotFound(AppException):
    def __init__(self, entity: str, entity_id: int):
        super().__init__(f"{entity} with id {entity_id} not found", 404)


class Conflict(AppException):
    def __init__(self, message: str):
        super().__init__(message, 409)


class Unauthorized(AppException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401)


class Forbidden(AppException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, 403)
