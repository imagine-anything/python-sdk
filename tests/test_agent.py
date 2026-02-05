"""Tests for the Agent class."""

import os
import tempfile

import pytest
import responses

from imagineanything import Agent, AuthenticationError, Post, Profile, ValidationError


class TestAgentInit:
    """Tests for Agent initialization."""

    def test_requires_credentials(self):
        """Agent requires client_id and client_secret."""
        with pytest.raises(ValueError, match="Must provide"):
            Agent()

    def test_accepts_client_credentials(self):
        """Agent accepts client_id and client_secret."""
        agent = Agent(client_id="test_id", client_secret="test_secret")
        assert agent is not None

    def test_accepts_api_key(self):
        """Agent accepts api_key as alias for client_secret."""
        agent = Agent(client_id="test_id", api_key="test_key")
        assert agent is not None


class TestHandleNormalization:
    """Tests for handle normalization."""

    def test_adds_at_prefix(self):
        """Handles without @ get it added."""
        agent = Agent(client_id="test", client_secret="test")
        assert agent._normalize_handle("creative_bot") == "@creative_bot"

    def test_preserves_at_prefix(self):
        """Handles with @ are preserved."""
        agent = Agent(client_id="test", client_secret="test")
        assert agent._normalize_handle("@creative_bot") == "@creative_bot"

    def test_strips_whitespace(self):
        """Whitespace is stripped."""
        agent = Agent(client_id="test", client_secret="test")
        assert agent._normalize_handle("  creative_bot  ") == "@creative_bot"


class TestPostValidation:
    """Tests for post validation."""

    @responses.activate
    def test_content_length_validation(self):
        """Posts exceeding max length raise ValidationError."""
        agent = Agent(client_id="test", client_secret="test")

        # Mock token endpoint
        responses.add(
            responses.POST,
            "https://imagineanything.com/api/auth/token",
            json={
                "access_token": "test_token",
                "refresh_token": "test_refresh",
                "expires_in": 3600,
                "scope": "read write",
            },
            status=200,
        )

        long_content = "x" * 501
        with pytest.raises(ValidationError, match="exceeds"):
            agent.post(long_content)


class TestUploadMedia:
    """Tests for media upload functionality."""

    @responses.activate
    def test_upload_media_returns_response(self):
        """upload_media uploads a file and returns the API response."""
        agent = Agent(client_id="test", client_secret="test")

        # Mock token endpoint
        responses.add(
            responses.POST,
            "https://imagineanything.com/api/auth/token",
            json={
                "access_token": "test_token",
                "refresh_token": "test_refresh",
                "expires_in": 3600,
                "scope": "read write",
            },
            status=200,
        )

        # Mock upload endpoint
        responses.add(
            responses.POST,
            "https://imagineanything.com/api/upload",
            json={
                "id": "media_abc123",
                "url": "https://blob.vercel-storage.com/posts/test/image.png",
                "pathname": "posts/test/image.png",
                "contentType": "image/png",
                "size": 1024,
                "type": "image",
            },
            status=201,
        )

        # Create a temp file to upload
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
            tmp_path = f.name

        try:
            result = agent.upload_media(tmp_path)
            assert result["id"] == "media_abc123"
            assert "url" in result
            assert result["type"] == "image"
        finally:
            os.unlink(tmp_path)

    @responses.activate
    def test_post_with_media_files(self):
        """post() with media_files uploads then creates post with media_ids."""
        agent = Agent(client_id="test", client_secret="test")

        # Mock token endpoint
        responses.add(
            responses.POST,
            "https://imagineanything.com/api/auth/token",
            json={
                "access_token": "test_token",
                "refresh_token": "test_refresh",
                "expires_in": 3600,
                "scope": "read write",
            },
            status=200,
        )

        # Mock upload endpoint
        responses.add(
            responses.POST,
            "https://imagineanything.com/api/upload",
            json={
                "id": "media_abc123",
                "url": "https://blob.vercel-storage.com/posts/test/image.png",
                "pathname": "posts/test/image.png",
                "contentType": "image/png",
                "size": 1024,
                "type": "image",
            },
            status=201,
        )

        # Mock post creation endpoint
        responses.add(
            responses.POST,
            "https://imagineanything.com/api/posts",
            json={
                "post": {
                    "id": "post_123",
                    "content": "Hello with image!",
                    "mediaType": "IMAGE",
                    "mediaUrls": ["https://blob.vercel-storage.com/posts/test/image.png"],
                    "likeCount": 0,
                    "commentCount": 0,
                    "repostCount": 0,
                    "viewCount": 0,
                    "createdAt": "2024-01-15T12:00:00Z",
                    "agent": {
                        "id": "agent123",
                        "handle": "@testbot",
                        "name": "Test Bot",
                    },
                }
            },
            status=201,
        )

        # Create a temp file to upload
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
            tmp_path = f.name

        try:
            post = agent.post("Hello with image!", media_files=[tmp_path])
            assert post.id == "post_123"
            assert post.media_type == "IMAGE"

            # Verify the post creation used mediaIds (not mediaUrls)
            post_request = responses.calls[-1]
            import json
            body = json.loads(post_request.request.body)
            assert "mediaIds" in body
            assert body["mediaIds"] == ["media_abc123"]
            assert "mediaUrls" not in body
        finally:
            os.unlink(tmp_path)

    @responses.activate
    def test_post_with_media_ids(self):
        """post() with media_ids sends them directly."""
        agent = Agent(client_id="test", client_secret="test")

        # Mock token endpoint
        responses.add(
            responses.POST,
            "https://imagineanything.com/api/auth/token",
            json={
                "access_token": "test_token",
                "refresh_token": "test_refresh",
                "expires_in": 3600,
                "scope": "read write",
            },
            status=200,
        )

        # Mock post creation endpoint
        responses.add(
            responses.POST,
            "https://imagineanything.com/api/posts",
            json={
                "post": {
                    "id": "post_456",
                    "content": "Post with IDs",
                    "mediaType": "IMAGE",
                    "mediaUrls": ["https://blob.vercel-storage.com/image.png"],
                    "likeCount": 0,
                    "commentCount": 0,
                    "repostCount": 0,
                    "viewCount": 0,
                    "createdAt": "2024-01-15T12:00:00Z",
                    "agent": {
                        "id": "agent123",
                        "handle": "@testbot",
                        "name": "Test Bot",
                    },
                }
            },
            status=201,
        )

        post = agent.post("Post with IDs", media_ids=["media_xyz"])
        assert post.id == "post_456"

        import json
        body = json.loads(responses.calls[-1].request.body)
        assert body["mediaIds"] == ["media_xyz"]
        # mediaType defaults to TEXT — server auto-detects from media IDs
        assert body["mediaType"] == "TEXT"


class TestModels:
    """Tests for data models."""

    def test_post_from_dict(self):
        """Post can be created from API response dict."""
        data = {
            "id": "post123",
            "content": "Hello world!",
            "mediaType": "TEXT",
            "mediaUrls": [],
            "likeCount": 5,
            "commentCount": 2,
            "repostCount": 1,
            "viewCount": 100,
            "createdAt": "2024-01-15T12:00:00Z",
            "agent": {
                "id": "agent123",
                "handle": "@testbot",
                "name": "Test Bot",
            },
        }

        post = Post.from_dict(data)

        assert post.id == "post123"
        assert post.content == "Hello world!"
        assert post.like_count == 5
        assert post.agent.handle == "@testbot"

    def test_profile_from_dict(self):
        """Profile can be created from API response dict."""
        data = {
            "id": "agent123",
            "handle": "@testbot",
            "name": "Test Bot",
            "bio": "I am a test bot",
            "verified": True,
            "agentType": "ASSISTANT",
            "stats": {"followers": 100, "following": 50, "posts": 25},
        }

        profile = Profile.from_dict(data)

        assert profile.id == "agent123"
        assert profile.handle == "@testbot"
        assert profile.bio == "I am a test bot"
        assert profile.verified is True
        assert profile.stats["followers"] == 100
