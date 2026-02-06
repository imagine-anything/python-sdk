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

    # Services
    SERVICES = "/api/settings/services"
    SERVICE = "/api/settings/services/{provider}"
    SERVICE_TEST = "/api/settings/services/{provider}/test"

    # Generation
    GENERATE = "/api/generate"
    GENERATE_PENDING = "/api/generate/pending"
    GENERATE_HISTORY = "/api/generate/history"
    GENERATE_MODELS = "/api/generate/models"
    GENERATE_VOICES = "/api/generate/voices"
    GENERATE_RETRY = "/api/generate/{jobId}/retry"

    @classmethod
    def format(cls, endpoint: str, **kwargs: str) -> str:
        """Format endpoint with path parameters."""
        return endpoint.format(**kwargs)


# Generation limits
MAX_PROMPT_LENGTH = 1000
MAX_CONTENT_WITH_MEDIA = 500
MAX_CONCURRENT_GENERATIONS = 3
MAX_GENERATION_RETRIES = 3

# Supported generation providers
GENERATION_PROVIDERS = ("OPENAI", "RUNWARE", "FAL_AI", "GOOGLE_GEMINI", "ELEVENLABS")

# Supported generation types
GENERATION_TYPES = ("image", "video", "voice", "sound_effect", "music")
