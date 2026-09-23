from pydantic import BaseModel


class ErrorSource(str, Enum):
    EXIT_CODE = "exit_code"
    ERRNO = "errno"
    SIGNAL = "signal"
    LOG_PATTERN = "log_pattern"
    EXCEPTION = "exception"
    EXTERNAL = "external"
    UNKNOWN = "unknown"


class ErrorToken(BaseModel):
    """A structured, searchable fingerprint of an error. Searches key on `normalized`."""

    normalized: str
    source: ErrorSource | None = None
    code: int | str | None = None
    raw: str | None = None
    locale: str | None = None
