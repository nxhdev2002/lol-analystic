"""
Unit tests for mini-fb-service publisher.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pika

from mini_fb_service.publisher import CookieChangedPublisher


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

    @patch("mini_fb_service.publisher.pika.BlockingConnection")
    def test_connect_success(self, mock_connection, publisher):
        """Test successful connection to RabbitMQ."""
        mock_channel = MagicMock()
        mock_conn = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn

        result = publisher.connect()

        assert result is True
        mock_connection.assert_called_once()
        mock_channel.exchange_declare.assert_called_once_with(
            exchange="test.events",
            exchange_type="topic",
            durable=True,
        )

    @patch("mini_fb_service.publisher.pika.BlockingConnection")
    def test_connect_failure(self, mock_connection, publisher):
        """Test failed connection to RabbitMQ."""
        mock_connection.side_effect = Exception("Connection failed")

        result = publisher.connect()

        assert result is False

    def test_disconnect(self, publisher):
        """Test disconnect method."""
        mock_channel = MagicMock()
        mock_conn = MagicMock()
        publisher._channel = mock_channel
        publisher._connection = mock_conn

        publisher.disconnect()

        mock_channel.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("mini_fb_service.publisher.pika.BlockingConnection")
    def test_publish_cookie_changed(self, mock_connection, publisher):
        """Test publishing cookie.changed event."""
        mock_channel = MagicMock()
        mock_conn = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn

        publisher.connect()

        result = publisher.publish_cookie_changed(
            account_id="test_account",
            new_cookie="datr=test123; xs=test456",
            old_cookie="old_cookie_value",
            force_reconnect=True,
        )

        assert result is True
        mock_channel.basic_publish.assert_called_once()
        call_args = mock_channel.basic_publish.call_args
        published_event = call_args[1]["body"]

        import json
        event = json.loads(published_event)
        assert event["event_type"] == "cookie.changed"
        assert event["data"]["account_id"] == "test_account"
        assert event["data"]["new_cookie"] == "datr=test123; xs=test456"
        assert event["data"]["old_cookie"] == "old_cookie_value"
        assert event["data"]["force_reconnect"] is True
        assert event["producer"] == "mini-fb-service"
        assert "event_id" in event

    @patch("mini_fb_service.publisher.pika.BlockingConnection")
    def test_publish_failure(self, mock_connection, publisher):
        """Test publish failure."""
        mock_channel = MagicMock()
        mock_channel.basic_publish.side_effect = Exception("Publish failed")
        mock_conn = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn

        publisher.connect()
        result = publisher.publish_cookie_changed(
            account_id="test_account",
            new_cookie="test_cookie",
        )

        assert result is False

    @patch("mini_fb_service.publisher.pika.BlockingConnection")
    def test_channel_property_reconnects(self, mock_connection, publisher):
        """Test that channel property reconnects if needed."""
        mock_channel = MagicMock()
        mock_channel.is_closed = True
        mock_conn = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn

        channel = publisher.channel

        assert channel is mock_channel
        mock_connection.assert_called_once()
