"""
Message send subscriber for OnMessageSendReceived event.
Consumes messages from RabbitMQ and sends them to Facebook Messenger.
"""

import logging
from typing import Callable, Optional, Dict, Any

from rabbitmq_client import BaseSubscriber, RabbitMQConnection
from config import QUEUE_MESSAGE_SEND
from events import MessageSendEvent

logger = logging.getLogger(__name__)


class MessageSendSubscriber(BaseSubscriber):
    """
    Subscriber for MessageSend events.
    Consumes messages from RabbitMQ and sends them to Facebook Messenger.
    """

    def __init__(
        self,
        connection: Optional[RabbitMQConnection] = None,
        send_callback: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ):
        """
        Initialize the message send subscriber.
        
        Args:
            connection: RabbitMQ connection instance. If None, creates a new one.
            send_callback: Callback function to send message to Facebook.
                           Should accept a dict with keys: recipient_id, recipient_type,
                           body, attachment_id, attachment_type.
                           Returns True if successful, False otherwise.
        """
        if connection is None:
            connection = RabbitMQConnection()
        
        # Default callback that just logs the event
        def default_callback(event: Dict[str, Any]):
            logger.info(f"Received message send event: {event}")
            # TODO: Implement actual Facebook message sending
            # This should call the Facebook API to send the message
        
        super().__init__(
            connection=connection,
            queue_name=QUEUE_MESSAGE_SEND,
            routing_key=QUEUE_MESSAGE_SEND,
            callback=send_callback or default_callback,
        )

    def validate_event(self, event: Dict[str, Any]) -> bool:
        """
        Validate the event structure.
        
        Args:
            event: Event dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            MessageSendEvent(**event)
            return True
        except Exception as e:
            logger.error(f"Invalid MessageSend event: {e}")
            return False

    def start(self):
        """Start consuming messages from the queue."""
        logger.info(f"Starting MessageSend subscriber on queue: {self.queue_name}")
        self.start_consuming()

    def stop(self):
        """Stop consuming messages from the queue."""
        logger.info(f"Stopping MessageSend subscriber on queue: {self.queue_name}")
        self.stop_consuming()
