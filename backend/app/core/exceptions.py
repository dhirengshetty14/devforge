class DevForgeError(Exception):
    """Base exception for application errors."""


class RateLimitExceeded(DevForgeError):
    """Raised when external API rate limit is exceeded."""


class ExternalServiceUnavailable(DevForgeError):
    """Raised when dependent service is unavailable."""
