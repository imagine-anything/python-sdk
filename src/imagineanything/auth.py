"""OAuth 2.0 token management for the ImagineAnything SDK."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import Lock
from typing import Optional

import requests

from .constants import Endpoints
from .exceptions import AuthenticationError


@dataclass
class TokenInfo:
    """OAuth token information."""

    access_token: str
    refresh_token: str
    expires_at: datetime
    scope: str


class TokenManager:
    """
    Manages OAuth 2.0 tokens with automatic refresh.

    Token lifecycle:
    1. First API call triggers token acquisition (client_credentials grant)
    2. Tokens cached in memory
    3. If auto_refresh enabled, refresh 5 minutes before expiry
    4. If token expired, transparently refresh using refresh_token
    """

    REFRESH_BUFFER = timedelta(minutes=5)

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str,
        auto_refresh: bool = True,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = base_url.rstrip("/")
        self._auto_refresh = auto_refresh
        self._token_info: Optional[TokenInfo] = None
        self._lock = Lock()

    def get_access_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.
        Thread-safe.
        """
        with self._lock:
            if self._token_info is None:
                self._acquire_token()
            elif self._should_refresh():
                self._refresh_token()
            if self._token_info is None:
                raise AuthenticationError("no_token", "Failed to acquire token")
            return self._token_info.access_token

    def _should_refresh(self) -> bool:
        """Check if token needs refresh."""
        if not self._auto_refresh or self._token_info is None:
            return False
        return datetime.utcnow() >= (self._token_info.expires_at - self.REFRESH_BUFFER)

    def _acquire_token(self) -> None:
        """Acquire token using client credentials grant."""
        response = requests.post(
            f"{self._base_url}{Endpoints.TOKEN}",
            json={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
            timeout=30,
        )
        self._handle_token_response(response)

    def _refresh_token(self) -> None:
        """Refresh token using refresh_token grant."""
        if self._token_info is None or not self._token_info.refresh_token:
            self._acquire_token()
            return

        response = requests.post(
            f"{self._base_url}{Endpoints.TOKEN}",
            json={
                "grant_type": "refresh_token",
                "refresh_token": self._token_info.refresh_token,
            },
            timeout=30,
        )
        # If refresh fails, try to acquire new token
        if response.status_code != 200:
            self._acquire_token()
            return
        self._handle_token_response(response)

    def _handle_token_response(self, response: requests.Response) -> None:
        """Parse token response and store token info."""
        if response.status_code != 200:
            try:
                data = response.json()
                error = data.get("error", "unknown_error")
                description = data.get(
                    "error_description", data.get("message", "Authentication failed")
                )
            except ValueError:
                error = "invalid_response"
                description = response.text or "Authentication failed"
            raise AuthenticationError(error=error, description=description)

        data = response.json()
        expires_at = datetime.utcnow() + timedelta(seconds=data["expires_in"])

        self._token_info = TokenInfo(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token", ""),
            expires_at=expires_at,
            scope=data.get("scope", "read write"),
        )

    def invalidate(self) -> None:
        """Force token re-acquisition on next request."""
        with self._lock:
            self._token_info = None
