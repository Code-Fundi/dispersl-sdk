class DisperslError(Exception):
    """Base SDK exception."""


class AuthenticationError(DisperslError):
    pass


class RateLimitError(DisperslError):
    def __init__(self, message: str, retry_after_seconds: int | None = None) -> None:
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


class ValidationError(DisperslError):
    pass


class NotFoundError(DisperslError):
    pass


class ConflictError(DisperslError):
    pass


class ServerError(DisperslError):
    pass


class RequestTimeoutError(DisperslError):
    pass


class StreamParseError(DisperslError):
    pass


class ToolExecutionError(DisperslError):
    pass
