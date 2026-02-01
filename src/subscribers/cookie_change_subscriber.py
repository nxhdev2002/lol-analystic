"""
Cookie change subscriber for OnCookieChanged event.
Consumes cookie change events from RabbitMQ and handles Facebook reconnection.
"""

import logging
from typing import Callable, Optional, Dict, Any

from rabbitmq_client import BaseSubscriber, RabbitMQConnection
from config import QUEUE_COOKIE_CHANGED
from events import CookieChangedEvent

logger = logging.getLogger(__name__)


class CookieChangeSubscriber(BaseSubscriber):
    """
    Subscriber for CookieChanged events.
    Consumes cookie change events from RabbitMQ and handles Facebook reconnection.
    """

    def __init__(
        self,
        connection: Optional[RabbitMQConnection] = None,
        reconnect_callback: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ):
        """
        Initialize the cookie change subscriber.
        
        Args:
            connection: RabbitMQ connection instance. If None, creates a new one.
            reconnect_callback: Callback function to handle Facebook reconnection.
                              Should accept a dict with keys: account_id, old_cookie,
                              new_cookie, force_reconnect.
                              Returns True if successful, False otherwise.
        """
        if connection is None:
            connection = RabbitMQConnection()
        
        # Default callback that just logs the event
        def default_callback(event: Dict[str, Any]):
            logger.info(f"Received cookie change event: {event}")
            # TODO: Implement actual Facebook reconnection
            # This should update the cookie and re-establish the Facebook connection
        
        super().__init__(
            connection=connection,
            queue_name=QUEUE_COOKIE_CHANGED,
            routing_key=QUEUE_COOKIE_CHANGED,
            callback=reconnect_callback or default_callback,
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
            CookieChangedEvent(**event)
            return True
        except Exception as e:
            logger.error(f"Invalid CookieChanged event: {e}")
            return False

    def start(self):
        """Start consuming messages from the queue."""
        logger.info(f"Starting CookieChange subscriber on queue: {self.queue_name}")
        self.start_consuming()

    def stop(self):
        """Stop consuming messages from the queue."""
        logger.info(f"Stopping CookieChange subscriber on queue: {self.queue_name}")
        self.stop_consuming()
