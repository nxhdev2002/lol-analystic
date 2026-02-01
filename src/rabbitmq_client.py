"""
RabbitMQ client module for managing connections, publishers, and subscribers.
Provides base classes for publishing and consuming events with automatic reconnection.
"""

import pika
import json
import logging
import threading
import time
from typing import Callable, Optional, Dict, Any
from abc import ABC, abstractmethod

from config import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_USER,
    RABBITMQ_PASSWORD,
    RABBITMQ_VHOST,
    RABBITMQ_EXCHANGE,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RabbitMQConnection:
    """
    Manages RabbitMQ connection with automatic reconnection logic.
    """

    def __init__(
        self,
        host: str = RABBITMQ_HOST,
        port: int = RABBITMQ_PORT,
        user: str = RABBITMQ_USER,
        password: str = RABBITMQ_PASSWORD,
        vhost: str = RABBITMQ_VHOST,
        exchange: str = RABBITMQ_EXCHANGE,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.vhost = vhost
        self.exchange = exchange
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None
        self._lock = threading.Lock()
        self._reconnect_delay = 5  # seconds
        self._max_reconnect_delay = 60  # seconds

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

    def reconnect(self):
        """Attempt to reconnect to RabbitMQ with exponential backoff."""
        while True:
            logger.info(f"Attempting to reconnect to RabbitMQ in {self._reconnect_delay} seconds...")
            time.sleep(self._reconnect_delay)
            
            if self.connect():
                self._reconnect_delay = 5  # Reset delay on success
                return True
            
            # Exponential backoff
            self._reconnect_delay = min(self._reconnect_delay * 2, self._max_reconnect_delay)

    @property
    def channel(self) -> Optional[pika.adapters.blocking_connection.BlockingChannel]:
        """Get the channel, reconnecting if necessary."""
        if self._channel is None or self._channel.is_closed:
            if not self.connect():
                return None
        return self._channel

    @property
    def connection(self) -> Optional[pika.BlockingConnection]:
        """Get the connection."""
        return self._connection


class BasePublisher(ABC):
    """
    Base class for RabbitMQ publishers.
    Handles connection management and message publishing.
    """

    def __init__(self, connection: RabbitMQConnection):
        self.connection = connection
        self._ensure_connected()

    def _ensure_connected(self):
        """Ensure connection is established."""
        if not self.connection.channel:
            self.connection.connect()

    def publish(self, routing_key: str, event: Dict[str, Any]) -> bool:
        """
        Publish an event to RabbitMQ.
        
        Args:
            routing_key: The routing key for the message
            event: The event dictionary to publish
            
        Returns:
            True if published successfully, False otherwise
        """
        try:
            channel = self.connection.channel
            if not channel:
                logger.error("No channel available for publishing")
                return False

            # Serialize event to JSON
            message = json.dumps(event, default=str)
            
            # Publish message
            channel.basic_publish(
                exchange=self.connection.exchange,
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            logger.debug(f"Published event to {routing_key}: {event.get('event_type')}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            # Attempt to reconnect
            self.connection.reconnect()
            return False


class BaseSubscriber(ABC):
    """
    Base class for RabbitMQ subscribers.
    Handles connection management and message consumption.
    """

    def __init__(
        self,
        connection: RabbitMQConnection,
        queue_name: str,
        routing_key: str,
        callback: Callable[[Dict[str, Any]], None],
        durable: bool = True,
    ):
        self.connection = connection
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.callback = callback
        self.durable = durable
        self._consuming = False

    def setup_queue(self) -> bool:
        """
        Declare the queue and bind it to the exchange.
        Returns True if successful, False otherwise.
        """
        try:
            channel = self.connection.channel
            if not channel:
                return False

            # Declare queue
            channel.queue_declare(
                queue=self.queue_name,
                durable=self.durable
            )
            
            # Bind queue to exchange with routing key
            channel.queue_bind(
                exchange=self.connection.exchange,
                queue=self.queue_name,
                routing_key=self.routing_key
            )
            
            # Set QoS to only process one message at a time
            channel.basic_qos(prefetch_count=1)
            
            logger.info(f"Queue {self.queue_name} set up with routing key {self.routing_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to set up queue: {e}")
            return False

    def _message_callback(self, channel, method, properties, body):
        """
        Internal callback wrapper for processing messages.
        """
        try:
            # Parse JSON message
            event = json.loads(body.decode('utf-8'))
            
            # Call the user callback
            self.callback(event)
            
            # Acknowledge message
            channel.basic_ack(delivery_tag=method.delivery_tag)
            logger.debug(f"Processed and acknowledged message from {self.queue_name}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message: {e}")
            # Reject message without requeue
            channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Reject message and requeue for retry
            channel.basic_reject(delivery_tag=method.delivery_tag, requeue=True)

    def start_consuming(self):
        """Start consuming messages from the queue."""
        try:
            if not self.setup_queue():
                logger.error("Failed to set up queue, cannot start consuming")
                return

            channel = self.connection.channel
            if not channel:
                return

            channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self._message_callback
            )
            
            self._consuming = True
            logger.info(f"Started consuming from queue: {self.queue_name}")
            channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopping consumption...")
            self.stop_consuming()
        except Exception as e:
            logger.error(f"Error in consumption: {e}")
            self.connection.reconnect()

    def stop_consuming(self):
        """Stop consuming messages from the queue."""
        if self._consuming:
            try:
                channel = self.connection.channel
                if channel:
                    channel.stop_consuming()
                self._consuming = False
                logger.info(f"Stopped consuming from queue: {self.queue_name}")
            except Exception as e:
                logger.error(f"Error stopping consumption: {e}")
