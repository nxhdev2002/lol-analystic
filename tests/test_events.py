"""
Unit tests for event schemas.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

# Add src to path to import event models
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from events import (
    BaseEvent,
    MessageReceivedEvent,
    MessageReceivedData,
    MessageSendEvent,
    MessageSendData,
    CookieChangedEvent,
    CookieChangedData,
    MatchEndedEvent,
    MatchEndedData,
    MessengerDisconnectedEvent,
    MessengerDisconnectedData,
)


class TestBaseEvent:
    """Tests for BaseEvent model."""

    def test_base_event_required_fields(self):
        """Test that BaseEvent has required fields."""
        event = BaseEvent(
            event_type="test.event",
            timestamp=datetime.utcnow(),
        )
        assert event.event_type == "test.event"
        assert isinstance(event.timestamp, datetime)

    def test_base_event_optional_fields(self):
        """Test that BaseEvent optional fields work."""
        event = BaseEvent(
            event_type="test.event",
            timestamp=datetime.utcnow(),
            event_id="123e4567-e89b-12d3-a456-426614174000",
            correlation_id="correlation-123",
            producer="test-service",
        )
        assert event.event_id == "123e4567-e89b-12d3-a456-426614174000"
        assert event.correlation_id == "correlation-123"
        assert event.producer == "test-service"


class TestMessageReceivedEvent:
    """Tests for MessageReceivedEvent model."""

    def test_message_received_event_valid(self):
        """Test valid MessageReceivedEvent."""
        event = MessageReceivedEvent(
            event_type="message.received",
            data={
                "message_id": "msg_123",
                "user_id": "user_456",
                "sender_id": "sender_789",
                "body": "Hello world",
                "reply_to_id": "thread_abc",
                "type": "thread",
                "attachments": [],
            },
        )
        assert event.event_type == "message.received"
        assert event.data.message_id == "msg_123"
        assert event.data.body == "Hello world"

    def test_message_received_data_validation(self):
        """Test MessageReceivedData validation."""
        data = MessageReceivedData(
            message_id="msg_123",
            user_id="user_456",
            sender_id="sender_789",
            body="Hello",
            reply_to_id="thread_abc",
            type="user",
            attachments=[{"type": "image", "url": "http://example.com/img.jpg"}],
        )
        assert data.attachments[0]["type"] == "image"


class TestMessageSendEvent:
    """Tests for MessageSendEvent model."""

    def test_message_send_event_valid(self):
        """Test valid MessageSendEvent."""
        event = MessageSendEvent(
            event_type="message.send",
            data={
                "recipient_id": "user_123",
                "recipient_type": "user",
                "body": "Hello back!",
            },
        )
        assert event.event_type == "message.send"
        assert event.data.recipient_id == "user_123"

    def test_message_send_data_validation(self):
        """Test MessageSendData validation."""
        data = MessageSendData(
            recipient_id="user_123",
            recipient_type="thread",
            body="Hello",
            attachment_id="att_456",
            attachment_type="image",
        )
        assert data.attachment_id == "att_456"


class TestCookieChangedEvent:
    """Tests for CookieChangedEvent model."""

    def test_cookie_changed_event_valid(self):
        """Test valid CookieChangedEvent."""
        event = CookieChangedEvent(
            event_type="cookie.changed",
            data={
                "account_id": "acc_123",
                "new_cookie": "datr=abc123; xs=def456",
                "force_reconnect": True,
            },
        )
        assert event.event_type == "cookie.changed"
        assert event.data.account_id == "acc_123"

    def test_cookie_changed_data_with_old_cookie(self):
        """Test CookieChangedData with old cookie."""
        data = CookieChangedData(
            account_id="acc_123",
            old_cookie="old_cookie_value",
            new_cookie="new_cookie_value",
            force_reconnect=False,
        )
        assert data.old_cookie == "old_cookie_value"
        assert data.force_reconnect is False


class TestMatchEndedEvent:
    """Tests for MatchEndedEvent model."""

    def test_match_ended_event_valid(self):
        """Test valid MatchEndedEvent."""
        event = MatchEndedEvent(
            event_type="match.ended",
            data={
                "match_id": "match_123",
                "puuid": "puuid_456",
                "summoner_name": "TestPlayer",
                "game_duration": 1800,
                "win": True,
                "champion": "Ahri",
                "kills": 10,
                "deaths": 5,
                "assists": 15,
                "kda": 5.0,
            },
        )
        assert event.event_type == "match.ended"
        assert event.data.win is True

    def test_match_ended_data_defaults(self):
        """Test MatchEndedData default values."""
        data = MatchEndedData(
            match_id="match_123",
            puuid="puuid_456",
            summoner_name="TestPlayer",
            game_duration=1800,
            win=True,
            champion="Ahri",
        )
        assert data.kills == 0
        assert data.deaths == 0
        assert data.assists == 0
        assert data.kda == 0.0


class TestMessengerDisconnectedEvent:
    """Tests for MessengerDisconnectedEvent model."""

    def test_messenger_disconnected_event_valid(self):
        """Test valid MessengerDisconnectedEvent."""
        event = MessengerDisconnectedEvent(
            event_type="messenger.disconnected",
            data={
                "account_id": "acc_123",
                "reason": "Connection timeout",
            },
        )
        assert event.event_type == "messenger.disconnected"
        assert event.data.reason == "Connection timeout"

    def test_messenger_disconnected_data_optional_reason(self):
        """Test MessengerDisconnectedData with optional reason."""
        data = MessengerDisconnectedData(account_id="acc_123")
        assert data.reason is None

        data_with_reason = MessengerDisconnectedData(
            account_id="acc_123", reason="Session expired"
        )
        assert data_with_reason.reason == "Session expired"
