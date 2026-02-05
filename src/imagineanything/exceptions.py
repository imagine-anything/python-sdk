"""Custom exceptions for the ImagineAnything SDK."""

from typing import Any, Dict, Optional


class ImagineAnythingError(Exception):
    """Base exception for all SDK errors."""

    pass


class AuthenticationError(ImagineAnythingError):
    """Authentication failed (invalid credentials or expired token)."""

    def __init__(self, error: str, description: str):
        self.error = error
        self.description = description
        super().__init__(f"{error}: {description}")


class APIError(ImagineAnythingError):
    """Base API error."""

    def __init__(
        self,
        error: str,
        message: str,
        status_code: int = 0,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.error = error
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(f"[{status_code}] {error}: {message}")


class NotFoundError(APIError):
    """Resource not found (404)."""

    def __init__(self, error: str, message: str):
        super().__init__(error, message, status_code=404)


class ValidationError(APIError):
    """Request validation failed (400)."""

    def __init__(
        self, error: str, message: str, details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(error, message, status_code=400, details=details)


class ForbiddenError(APIError):
    """Access denied (403)."""

    def __init__(self, error: str, message: str):
        super().__init__(error, message, status_code=403)


class RateLimitError(APIError):
    """Rate limit exceeded (429)."""

    def __init__(
        self,
        error: str,
        message: str,
        retry_after: Optional[int] = None,
    ):
        super().__init__(error, message, status_code=429)
        self.retry_after = retry_after


class ServerError(APIError):
    """Server error (5xx)."""

    pass
