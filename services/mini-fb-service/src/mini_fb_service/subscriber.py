"""
Messenger disconnected subscriber for mini-fb-service.
Consumes messenger.disconnected events and triggers automated login.
"""

import logging
import os
import sys
from typing import Callable, Optional

import pika
import pika.exceptions

# Import sibling module - use absolute import for compatibility
sys.path.insert(0, os.path.dirname(__file__))
from publisher import CookieChangedPublisher

logger = logging.getLogger(__name__)


class MessengerDisconnectedSubscriber:
    """
    Subscriber for MessengerDisconnected events.
    Triggers automated login when fbchat-core reports disconnection.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5672,
        user: str = "guest",
        password: str = "guest",
        vhost: str = "/",
        exchange: str = "fbchat.events",
        login_callback: Optional[Callable] = None,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.vhost = vhost
        self.exchange = exchange
        self.login_callback = login_callback
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None
        self._consuming = False
        self._cookie_publisher: Optional[CookieChangedPublisher] = None

    def connect(self) -> bool:
        """
        Establish connection to RabbitMQ server.
        Returns True if connection successful, False otherwise.
        """
        # Import config - handle both local and Docker execution
        try:
            from _shared.config import (
                RABBITMQ_HOST,
                RABBITMQ_PORT,
                RABBITMQ_USER,
                RABBITMQ_PASSWORD,
                RABBITMQ_VHOST,
                RABBITMQ_EXCHANGE,
            )
        except ImportError:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
            from _shared.config import (
                RABBITMQ_HOST,
                RABBITMQ_PORT,
                RABBITMQ_USER,
                RABBITMQ_PASSWORD,
                RABBITMQ_VHOST,
                RABBITMQ_EXCHANGE,
            )

        try:
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
            parameters = pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                virtual_host=RABBITMQ_VHOST,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
            )
            self._connection = pika.BlockingConnection(parameters)
            self._channel = self._connection.channel()
            
            # Declare exchange
            self._channel.exchange_declare(
                exchange=RABBITMQ_EXCHANGE,
                exchange_type='topic',
                durable=True
            )
            
            # Declare exclusive queue for this service
            result = self._channel.queue_declare(
                queue='mini-fb-service.messenger.disconnected',
                durable=True
            )
            queue_name = result.method.queue
            
            # Bind queue to exchange with routing key
            self._channel.queue_bind(
                exchange=RABBITMQ_EXCHANGE,
                queue=queue_name,
                routing_key='messenger.disconnected'
            )
            
            # Set QoS to only process one message at a time
            self._channel.basic_qos(prefetch_count=1)
            
            logger.info(f"Connected to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}")
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

    def _message_callback(self, channel, method, properties, body):
        """
        Internal callback wrapper for processing messages.
        """
        try:
            import json
            event = json.loads(body.decode('utf-8'))

            logger.info(f"Received messenger.disconnected event: {event.get('data', {})}")

            # Extract account ID from event
            account_id = event.get('data', {}).get('account_id')
            reason = event.get('data', {}).get('reason')

            if not account_id:
                logger.error("Missing account_id in messenger.disconnected event")
                channel.basic_ack(delivery_tag=method.delivery_tag)
                return

            # Trigger login callback
            if self.login_callback:
                try:
                    new_cookie = self.login_callback(account_id, reason)
                    if new_cookie:
                        # Publish cookie.changed event
                        if not self._cookie_publisher:
                            self._cookie_publisher = CookieChangedPublisher(
                                host=self.host,
                                port=self.port,
                                user=self.user,
                                password=self.password,
                                vhost=self.vhost,
                                exchange=self.exchange,
                            )
                            self._cookie_publisher.connect()

                        self._cookie_publisher.publish_cookie_changed(
                            account_id=account_id,
                            new_cookie=new_cookie,
                            force_reconnect=True,
                        )
                except Exception as e:
                    logger.error(f"Error in login callback: {e}")

            # Acknowledge message
            channel.basic_ack(delivery_tag=method.delivery_tag)
            logger.debug(f"Processed and acknowledged messenger.disconnected message")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message: {e}")
            channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            channel.basic_reject(delivery_tag=method.delivery_tag, requeue=True)

    def start_consuming(self):
        """Start consuming messages from the queue."""
        try:
            if not self.connect():
                logger.error("Failed to set up queue, cannot start consuming")
                return

            self._channel.basic_consume(
                queue='mini-fb-service.messenger.disconnected',
                on_message_callback=self._message_callback
            )

            logger.info("Starting MessengerDisconnected subscriber...")
            self._consuming = True
            self._channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopping subscriber...")
            self.stop_consuming()
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")
            self.stop_consuming()

    def stop_consuming(self):
        """Stop consuming messages from the queue."""
        try:
            if self._channel and self._consuming:
                self._channel.stop_consuming()
                self._consuming = False
                logger.info("Stopped MessengerDisconnected subscriber")
        except Exception as e:
            logger.error(f"Error stopping consumer: {e}")
