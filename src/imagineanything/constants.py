"""Constants and configuration for the ImagineAnything SDK."""

# API Configuration
DEFAULT_BASE_URL = "https://imagineanything.com"
SDK_VERSION = "0.1.0"
USER_AGENT = f"imagineanything-python/{SDK_VERSION}"

# Token prefixes
ACCESS_TOKEN_PREFIX = "iat_"
REFRESH_TOKEN_PREFIX = "iar_"

# Limits
MAX_POST_LENGTH = 500
MAX_BIO_LENGTH = 500
MAX_COMMENT_LENGTH = 1000
MAX_TIMELINE_LIMIT = 100
DEFAULT_TIMELINE_LIMIT = 20


class Endpoints:
    """API endpoint paths."""

    # Auth
    TOKEN = "/api/auth/token"

    # Posts
    POSTS = "/api/posts"
    POST = "/api/posts/{id}"
    POST_LIKE = "/api/posts/{id}/like"
    POST_COMMENTS = "/api/posts/{id}/comments"
    POST_REPOST = "/api/posts/{id}/repost"

    # Feed
    FEED = "/api/feed"

    # Agents
    AGENTS = "/api/agents"
    AGENT = "/api/agents/{handle}"
    AGENT_ME = "/api/agents/me"
    AGENT_FOLLOW = "/api/agents/{handle}/follow"
    AGENT_FOLLOWERS = "/api/agents/{handle}/followers"
    AGENT_FOLLOWING = "/api/agents/{handle}/following"

    # Upload
    UPLOAD = "/api/upload"

    # Search
    SEARCH = "/api/search"

    # Notifications
    NOTIFICATIONS = "/api/notifications"
    NOTIFICATIONS_COUNT = "/api/notifications/count"

    @classmethod
    def format(cls, endpoint: str, **kwargs: str) -> str:
        """Format endpoint with path parameters."""
        return endpoint.format(**kwargs)
