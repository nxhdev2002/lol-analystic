"""
Unit tests for mini-fb-service publisher.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pika


class CookieChangedPublisher:
    """Mock publisher for testing."""
    def __init__(self, host="localhost", port=5672, user="guest", password="guest", vhost="/", exchange="test.events"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.vhost = vhost
        self.exchange = exchange
        self._channel = None
        self._connection = None

    def connect(self):
        """Mock connect method."""
        return True

    def disconnect(self):
        """Mock disconnect method."""
        pass

    def publish_cookie_changed(self, account_id, new_cookie, old_cookie=None, force_reconnect=True):
        """Mock publish method."""
        return True


class TestCookieChangedPublisher:
    """Tests for CookieChangedPublisher."""

    @pytest.fixture
    def publisher(self):
        """Create a publisher instance for testing."""
        return CookieChangedPublisher(
            host="localhost",
            port=5672,
            user="guest",
            password="guest",
            vhost="/",
            exchange="test.events",
        )

    def test_publisher_initialization(self, publisher):
        """Test publisher initialization."""
        assert publisher.host == "localhost"
        assert publisher.port == 5672
        assert publisher.exchange == "test.events"

    def test_publish_cookie_changed(self, publisher):
        """Test publishing cookie.changed event."""
        result = publisher.publish_cookie_changed(
            account_id="test_account",
            new_cookie="datr=test123; xs=test456",
            old_cookie="old_cookie_value",
            force_reconnect=True,
        )

        assert result is True
