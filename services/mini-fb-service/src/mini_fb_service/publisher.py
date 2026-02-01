"""
Cookie change publisher for mini-fb-service.
Publishes cookie.changed events to RabbitMQ after successful login.
"""

import logging
import uuid
from typing import Optional
from datetime import datetime

import pika
import pika.exceptions

logger = logging.getLogger(__name__)


class CookieChangedPublisher:
    """
    Publisher for CookieChanged events.
    Publishes cookie updates after successful Facebook login.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5672,
        user: str = "guest",
        password: str = "guest",
        vhost: str = "/",
        exchange: str = "fbchat.events",
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.vhost = vhost
        self.exchange = exchange
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None

    def connect(self) -> bool:
        """
        Establish connection to RabbitMQ server.
        Returns True if connection successful, False otherwise.
        """
        try:
            credentials = pika.PlainCredentials(self.user, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.vhost,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
            )
            self._connection = pika.BlockingConnection(parameters)
            self._channel = self._connection.channel()

            # Declare exchange
            self._channel.exchange_declare(
                exchange=self.exchange,
                exchange_type='topic',
                durable=True
            )

            logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False

    def disconnect(self):
        """Close the connection to RabbitMQ."""
        try:
            if self._channel and not self._channel.is_closed:
                self._channel.close()
            if self._connection and not self._connection.is_closed:
                self._connection.close()
            logger.info("Disconnected from RabbitMQ")
        except Exception as e:
            logger.error(f"Error disconnecting from RabbitMQ: {e}")

    def publish_cookie_changed(
        self,
        account_id: str,
        new_cookie: str,
        old_cookie: Optional[str] = None,
        force_reconnect: bool = True,
    ) -> bool:
        """
        Publish a CookieChanged event.

        Args:
            account_id: Facebook account ID
            new_cookie: New cookie value
            old_cookie: Old cookie value (optional)
            force_reconnect: Force reconnection flag

        Returns:
            True if published successfully, False otherwise
        """
        try:
            event = {
                "event_type": "cookie.changed",
                "event_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "producer": "mini-fb-service",
                "data": {
                    "account_id": account_id,
                    "old_cookie": old_cookie,
                    "new_cookie": new_cookie,
                    "force_reconnect": force_reconnect,
                }
            }

            import json
            message = json.dumps(event, default=str)

            self._channel.basic_publish(
                exchange=self.exchange,
                routing_key="cookie.changed",
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )

            logger.info(f"Published cookie.changed event for account {account_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish cookie.changed event: {e}")
            return False

    @property
    def channel(self):
        """Get the channel, connecting if necessary."""
        if self._channel is None or self._channel.is_closed:
            self.connect()
        return self._channel
