"""
Message publisher for OnMessageReceived event.
Publishes received Facebook messages to RabbitMQ.
"""

import logging
from typing import Dict, Any, Optional

from rabbitmq_client import BasePublisher, RabbitMQConnection
from config import QUEUE_MESSAGE_RECEIVED, QUEUE_MESSENGER_DISCONNECTED
from events import MessageReceivedEvent, MessengerDisconnectedEvent

logger = logging.getLogger(__name__)


class MessagePublisher(BasePublisher):
    """
    Publisher for MessageReceived events.
    Publishes messages received from Facebook to RabbitMQ.
    """

    def __init__(self, connection: Optional[RabbitMQConnection] = None):
        """
        Initialize the message publisher.
        
        Args:
            connection: RabbitMQ connection instance. If None, creates a new one.
        """
        if connection is None:
            connection = RabbitMQConnection()
        super().__init__(connection)

    def publish_message_received(
        self,
        message_id: str,
        user_id: str,
        sender_id: str,
        body: str,
        reply_to_id: str,
        message_type: str,
        attachments: Optional[list] = None,
    ) -> bool:
        """
        Publish a MessageReceived event.
        
        Args:
            message_id: Unique message identifier
            user_id: User ID who sent the message
            sender_id: Sender ID
            body: Message content
            reply_to_id: Thread or user ID to reply to
            message_type: Message type: 'user' or 'thread'
            attachments: List of attachments (optional)
            
        Returns:
            True if published successfully, False otherwise
        """
        try:
            # Create event using Pydantic model
            event = MessageReceivedEvent(
                event_type="message.received",
                data={
                    "message_id": message_id,
                    "user_id": user_id,
                    "sender_id": sender_id,
                    "body": body,
                    "reply_to_id": reply_to_id,
                    "type": message_type,
                    "attachments": attachments or [],
                },
                producer="fbchat-core",
            )
            
            # Convert to dict for publishing
            event_dict = event.model_dump()
            
            # Publish to RabbitMQ
            return self.publish(
                routing_key=QUEUE_MESSAGE_RECEIVED,
                event=event_dict
            )
        except Exception as e:
            logger.error(f"Failed to publish MessageReceived event: {e}")
            return False

    def publish_from_dict(self, message_data: Dict[str, Any]) -> bool:
        """
        Publish a MessageReceived event from a dictionary.
        
        Args:
            message_data: Dictionary containing message data with keys:
                - message_id
                - user_id
                - sender_id
                - body
                - reply_to_id
                - type
                - attachments (optional)
                
        Returns:
            True if published successfully, False otherwise
        """
        try:
            return self.publish_message_received(
                message_id=message_data.get("message_id", ""),
                user_id=message_data.get("user_id", ""),
                sender_id=message_data.get("sender_id", ""),
                body=message_data.get("body", ""),
                reply_to_id=message_data.get("reply_to_id", ""),
                message_type=message_data.get("type", "thread"),
                attachments=message_data.get("attachments", []),
            )
        except Exception as e:
            logger.error(f"Failed to publish message from dict: {e}")
            return False

    def publish_messenger_disconnected(
        self,
        account_id: str,
        reason: Optional[str] = None,
    ) -> bool:
        """
        Publish a MessengerDisconnected event.
        
        Args:
            account_id: Facebook account ID
            reason: Reason for disconnection (optional)
            
        Returns:
            True if published successfully, False otherwise
        """
        try:
            import uuid
            # Create event using Pydantic model
            event = MessengerDisconnectedEvent(
                event_type="messenger.disconnected",
                data={
                    "account_id": account_id,
                    "reason": reason,
                },
                event_id=str(uuid.uuid4()),
                producer="fbchat-core",
            )
            
            # Convert to dict for publishing
            event_dict = event.model_dump()
            
            # Publish to RabbitMQ
            return self.publish(
                routing_key=QUEUE_MESSENGER_DISCONNECTED,
                event=event_dict
            )
        except Exception as e:
            logger.error(f"Failed to publish MessengerDisconnected event: {e}")
            return False
