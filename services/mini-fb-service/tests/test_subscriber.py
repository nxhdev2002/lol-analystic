"""
Unit tests for mini-fb-service subscriber.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import pika

from mini_fb_service.subscriber import MessengerDisconnectedSubscriber


class TestMessengerDisconnectedSubscriber:
    """Tests for MessengerDisconnectedSubscriber."""

    @pytest.fixture
    def subscriber(self):
        """Create a subscriber instance for testing."""
        return MessengerDisconnectedSubscriber(
            host="localhost",
            port=5672,
            user="guest",
            password="guest",
            vhost="/",
            exchange="test.events",
        )

    def test_subscriber_initialization(self, subscriber):
        """Test subscriber initialization."""
        assert subscriber.host == "localhost"
        assert subscriber.port == 5672
        assert subscriber.exchange == "test.events"

    @patch("mini_fb_service.subscriber.pika.BlockingConnection")
    def test_connect_success(self, mock_connection, subscriber):
        """Test successful connection to RabbitMQ."""
        mock_channel = MagicMock()
        mock_conn = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn

        result = subscriber.connect()

        assert result is True
        mock_connection.assert_called_once()
        mock_channel.queue_declare.assert_called_once_with(
            queue='mini-fb-service.messenger.disconnected',
            durable=True
        )
        mock_channel.queue_bind.assert_called_once_with(
            exchange="test.events",
            queue='mini-fb-service.messenger.disconnected',
            routing_key='messenger.disconnected'
        )
        mock_channel.basic_qos.assert_called_once_with(prefetch_count=1)

    @patch("mini_fb_service.subscriber.pika.BlockingConnection")
    def test_connect_failure(self, mock_connection, subscriber):
        """Test failed connection to RabbitMQ."""
        mock_connection.side_effect = Exception("Connection failed")

        result = subscriber.connect()

        assert result is False

    def test_disconnect(self, subscriber):
        """Test disconnect method."""
        mock_channel = MagicMock()
        mock_conn = MagicMock()
        subscriber._channel = mock_channel
        subscriber._connection = mock_conn

        subscriber.disconnect()

        mock_channel.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("mini_fb_service.subscriber.pika.BlockingConnection")
    def test_message_callback_valid_event(self, mock_connection, subscriber):
        """Test processing a valid messenger.disconnected event."""
        mock_channel = MagicMock()
        mock_conn = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn

        subscriber.connect()

        # Mock login callback
        mock_login_callback = Mock(return_value="new_cookie_value")
        subscriber.login_callback = mock_login_callback

        # Mock cookie publisher
        mock_publisher = MagicMock()
        subscriber._cookie_publisher = mock_publisher

        # Create mock event
        import json
        event = {
            "event_type": "messenger.disconnected",
            "data": {
                "account_id": "test_account",
                "reason": "Connection timeout",
            }
        }

        # Call internal callback
        method = MagicMock()
        method.delivery_tag = 1
        properties = MagicMock()
        body = json.dumps(event).encode('utf-8')

        subscriber._message_callback(mock_channel, method, properties, body)

        # Verify login callback was called
        mock_login_callback.assert_called_once_with(
            "test_account", "Connection timeout"
        )

        # Verify cookie was published
        mock_publisher.publish_cookie_changed.assert_called_once_with(
            account_id="test_account",
            new_cookie="new_cookie_value",
            force_reconnect=True,
        )

        # Verify message was acknowledged
        mock_channel.basic_ack.assert_called_once_with(delivery_tag=1)

    @patch("mini_fb_service.subscriber.pika.BlockingConnection")
    def test_message_callback_missing_account_id(self, mock_connection, subscriber):
        """Test handling event with missing account_id."""
        mock_channel = MagicMock()
        mock_conn = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn

        subscriber.connect()

        # Mock login callback
        mock_login_callback = Mock()
        subscriber.login_callback = mock_login_callback

        # Create mock event without account_id
        import json
        event = {
            "event_type": "messenger.disconnected",
            "data": {
                "reason": "Connection timeout",
            }
        }

        method = MagicMock()
        method.delivery_tag = 1
        properties = MagicMock()
        body = json.dumps(event).encode('utf-8')

        subscriber._message_callback(mock_channel, method, properties, body)

        # Verify login callback was NOT called
        mock_login_callback.assert_not_called()

        # Verify message was still acknowledged
        mock_channel.basic_ack.assert_called_once_with(delivery_tag=1)

    @patch("mini_fb_service.subscriber.pika.BlockingConnection")
    def test_message_callback_login_failure(self, mock_connection, subscriber):
        """Test handling login callback failure."""
        mock_channel = MagicMock()
        mock_conn = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn

        subscriber.connect()

        # Mock login callback that returns None (failure)
        mock_login_callback = Mock(return_value=None)
        subscriber.login_callback = mock_login_callback

        # Mock cookie publisher
        mock_publisher = MagicMock()
        subscriber._cookie_publisher = mock_publisher

        # Create mock event
        import json
        event = {
            "event_type": "messenger.disconnected",
            "data": {
                "account_id": "test_account",
                "reason": "Connection timeout",
            }
        }

        method = MagicMock()
        method.delivery_tag = 1
        properties = MagicMock()
        body = json.dumps(event).encode('utf-8')

        subscriber._message_callback(mock_channel, method, properties, body)

        # Verify cookie was NOT published
        mock_publisher.publish_cookie_changed.assert_not_called()

        # Verify message was still acknowledged
        mock_channel.basic_ack.assert_called_once_with(delivery_tag=1)

    @patch("mini_fb_service.subscriber.pika.BlockingConnection")
    def test_message_callback_invalid_json(self, mock_connection, subscriber):
        """Test handling invalid JSON message."""
        mock_channel = MagicMock()
        mock_conn = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn

        subscriber.connect()

        method = MagicMock()
        method.delivery_tag = 1
        properties = MagicMock()
        body = b"invalid json"

        subscriber._message_callback(mock_channel, method, properties, body)

        # Verify message was rejected without requeue
        mock_channel.basic_reject.assert_called_once_with(
            delivery_tag=1, requeue=False
        )

    @patch("mini_fb_service.subscriber.pika.BlockingConnection")
    def test_start_consuming(self, mock_connection, subscriber):
        """Test start_consuming method."""
        mock_channel = MagicMock()
        mock_conn = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn

        with patch.object(subscriber, "connect", return_value=True):
            subscriber.start_consuming()

        mock_channel.basic_consume.assert_called_once()
        mock_channel.start_consuming.assert_called_once()

    @patch("mini_fb_service.subscriber.pika.BlockingConnection")
    def test_stop_consuming(self, mock_connection, subscriber):
        """Test stop_consuming method."""
        mock_channel = MagicMock()
        mock_conn = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn

        subscriber._consuming = True
        subscriber._channel = mock_channel

        subscriber.stop_consuming()

        mock_channel.stop_consuming.assert_called_once()
        assert subscriber._consuming is False
