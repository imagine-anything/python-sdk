"""HTTP client for the ImagineAnything API."""

from typing import Any, Dict, Optional

import requests

from .auth import TokenManager
from .constants import USER_AGENT
from .exceptions import (
    APIError,
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


class APIClient:
    """
    Low-level HTTP client for ImagineAnything API.
    Handles authentication headers and error translation.
    """

    def __init__(
        self,
        token_manager: TokenManager,
        base_url: str,
        timeout: float = 30.0,
    ) -> None:
        self._token_manager = token_manager
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
            }
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        authenticated: bool = True,
    ) -> Dict[str, Any]:
        """
        Make an API request.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            path: API path (e.g., "/api/posts")
            params: Query parameters
            json: JSON body
            authenticated: Whether to include auth header

        Returns:
            Parsed JSON response

        Raises:
            APIError: On API error responses
        """
        url = f"{self._base_url}{path}"
        headers: Dict[str, str] = {}

        if authenticated:
            token = self._token_manager.get_access_token()
            headers["Authorization"] = f"Bearer {token}"

        response = self._session.request(
            method=method,
            url=url,
            params=params,
            json=json,
            headers=headers,
            timeout=self._timeout,
        )

        return self._handle_response(response)

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle response and raise appropriate exceptions."""
        if response.status_code == 204:
            return {}

        try:
            data: Dict[str, Any] = response.json()
        except ValueError:
            data = {"error": "invalid_response", "message": response.text}

        if response.status_code >= 400:
            self._raise_for_status(response.status_code, data)

        return data

    def _raise_for_status(self, status: int, data: Dict[str, Any]) -> None:
        """Raise appropriate exception for error status."""
        error = data.get("error", "unknown_error")
        message = data.get("message", data.get("error_description", "Unknown error"))

        if status == 401:
            self._token_manager.invalidate()
            raise AuthenticationError(error=error, description=message)
        elif status == 403:
            raise ForbiddenError(error=error, message=message)
        elif status == 404:
            raise NotFoundError(error=error, message=message)
        elif status == 400:
            raise ValidationError(error=error, message=message, details=data)
        elif status == 429:
            raise RateLimitError(
                error=error,
                message=message,
                retry_after=data.get("retry_after"),
            )
        elif status >= 500:
            raise ServerError(error=error, message=message, status_code=status)
        else:
            raise APIError(error=error, message=message, status_code=status)

    def upload(
        self,
        path: str,
        file_path: str,
        *,
        fields: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Upload a file via multipart/form-data.

        Args:
            path: API path (e.g., "/api/upload")
            file_path: Local path to the file to upload
            fields: Additional form fields

        Returns:
            Parsed JSON response
        """
        import mimetypes
        import os

        url = f"{self._base_url}{path}"
        token = self._token_manager.get_access_token()

        filename = os.path.basename(file_path)
        content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

        with open(file_path, "rb") as f:
            files = {"file": (filename, f, content_type)}
            data = fields or {}
            # Use a separate request (not session) to avoid session's
            # Content-Type: application/json header interfering with multipart
            response = requests.post(
                url=url,
                files=files,
                data=data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "User-Agent": USER_AGENT,
                },
                timeout=self._timeout,
            )

        return self._handle_response(response)

    def get(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make a GET request."""
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make a POST request."""
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make a PUT request."""
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make a PATCH request."""
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self.request("DELETE", path, **kwargs)
