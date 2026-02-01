"""
Event schemas for RabbitMQ message validation using Pydantic.
All events follow a consistent structure with event_type, timestamp, and data fields.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    """Base class for all events."""
    event_type: str = Field(..., description="Type of the event")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    event_id: Optional[str] = Field(None, description="Unique event identifier (UUID)")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracing across services")
    producer: Optional[str] = Field(None, description="Service name that produced the event")


class MessageReceivedData(BaseModel):
    """Data structure for MessageReceived event."""
    message_id: str = Field(..., description="Unique message identifier")
    user_id: str = Field(..., description="User ID who sent the message")
    sender_id: str = Field(..., description="Sender ID")
    body: str = Field(..., description="Message content")
    reply_to_id: str = Field(..., description="Thread or user ID to reply to")
    type: str = Field(..., description="Message type: 'user' or 'thread'")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="List of attachments")


class MessageReceivedEvent(BaseEvent):
    """Event published when a message is received from Facebook."""
    event_type: str = "message.received"
    data: MessageReceivedData


class MessageSendData(BaseModel):
    """Data structure for MessageSend event."""
    recipient_id: str = Field(..., description="Recipient ID")
    recipient_type: str = Field(..., description="Recipient type: 'user' or 'thread'")
    body: str = Field(..., description="Message content to send")
    attachment_id: Optional[str] = Field(None, description="Attachment ID if any")
    attachment_type: Optional[str] = Field(None, description="Attachment type if any")


class MessageSendEvent(BaseEvent):
    """Event consumed to send a message to Facebook Messenger."""
    event_type: str = "message.send"
    data: MessageSendData


class CookieChangedData(BaseModel):
    """Data structure for CookieChanged event."""
    account_id: str = Field(..., description="Facebook account ID")
    old_cookie: Optional[str] = Field(None, description="Old cookie value")
    new_cookie: str = Field(..., description="New cookie value")
    force_reconnect: bool = Field(default=True, description="Force reconnection flag")


class CookieChangedEvent(BaseEvent):
    """Event consumed when a cookie change is detected."""
    event_type: str = "cookie.changed"
    data: CookieChangedData


class MatchEndedData(BaseModel):
    """Data structure for MatchEnded event."""
    match_id: str = Field(..., description="Riot match ID")
    puuid: str = Field(..., description="Player PUUID")
    summoner_name: str = Field(..., description="Summoner name")
    game_duration: int = Field(..., description="Game duration in seconds")
    win: bool = Field(..., description="True if player won the match")
    champion: str = Field(..., description="Champion played")
    kills: int = Field(default=0, description="Number of kills")
    deaths: int = Field(default=0, description="Number of deaths")
    assists: int = Field(default=0, description="Number of assists")
    kda: float = Field(default=0.0, description="KDA ratio")


class MatchEndedEvent(BaseEvent):
    """Event published when a match ends."""
    event_type: str = "match.ended"
    data: MatchEndedData


class MessengerDisconnectedData(BaseModel):
    """Data structure for MessengerDisconnected event."""
    account_id: str = Field(..., description="Facebook account ID")
    reason: Optional[str] = Field(None, description="Reason for disconnection")


class MessengerDisconnectedEvent(BaseEvent):
    """Event published when Facebook Messenger MQTT connection is disconnected."""
    event_type: str = "messenger.disconnected"
    data: MessengerDisconnectedData


# Event type mapping for easy reference
EVENT_TYPES = {
    "message.received": MessageReceivedEvent,
    "message.send": MessageSendEvent,
    "cookie.changed": CookieChangedEvent,
    "match.ended": MatchEndedEvent,
    "messenger.disconnected": MessengerDisconnectedEvent,
}
