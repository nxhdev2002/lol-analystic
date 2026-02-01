"""
Main entry point for mini-fb-service.
Subscribes to messenger.disconnected events and triggers automated login.
"""

import logging

# Import config - handle both local and Docker execution
try:
    from _shared.config import (
        MINIFB_ACCOUNT,
        MINIFB_PASSWORD,
        MINIFB_HEADLESS,
        MINIFB_CHROME_VERSION,
        MINIFB_USER_DATA_DIR,
        MINIFB_PROXY,
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
        MINIFB_ACCOUNT,
        MINIFB_PASSWORD,
        MINIFB_HEADLESS,
        MINIFB_CHROME_VERSION,
        MINIFB_USER_DATA_DIR,
        MINIFB_PROXY,
        RABBITMQ_HOST,
        RABBITMQ_PORT,
        RABBITMQ_USER,
        RABBITMQ_PASSWORD,
        RABBITMQ_VHOST,
        RABBITMQ_EXCHANGE,
    )

# Import sibling modules - use absolute imports for compatibility
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from browser import FacebookBrowser
from subscriber import MessengerDisconnectedSubscriber

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def perform_login(account_id: str, reason: str = None) -> str:
    """
    Perform automated Facebook login.

    Args:
        account_id: Facebook account ID (from event)
        reason: Reason for relogin (from event)

    Returns:
        New cookie string if successful, None otherwise
    """
    logger.info(f"Triggering automated login for account {account_id} (reason: {reason})")

    email = MINIFB_ACCOUNT
    password = MINIFB_PASSWORD

    if not email or not password:
        logger.error("MINIFB_ACCOUNT and MINIFB_PASSWORD environment variables are required")
        return None

    headless = MINIFB_HEADLESS
    chrome_version = MINIFB_CHROME_VERSION
    user_data_dir = MINIFB_USER_DATA_DIR
    proxy = MINIFB_PROXY

    try:
        with FacebookBrowser(headless=headless, chrome_version=chrome_version, user_data_dir=user_data_dir, proxy=proxy) as browser:
            cookie = browser.login(email, password)

            if cookie:
                logger.info(f"Successfully logged in and extracted cookie")
                return cookie
            else:
                logger.error("Failed to login or extract cookie")
                return None

    except Exception as e:
        logger.error(f"Error during automated login: {e}")
        return None


def main():
    """Main entry point."""
    logger.info("Starting mini-fb-service...")

    # Get RabbitMQ configuration from shared config
    rabbitmq_host = RABBITMQ_HOST
    rabbitmq_port = RABBITMQ_PORT
    rabbitmq_user = RABBITMQ_USER
    rabbitmq_password = RABBITMQ_PASSWORD
    rabbitmq_vhost = RABBITMQ_VHOST
    rabbitmq_exchange = RABBITMQ_EXCHANGE

    # Create subscriber
    subscriber = MessengerDisconnectedSubscriber(
        host=rabbitmq_host,
        port=rabbitmq_port,
        user=rabbitmq_user,
        password=rabbitmq_password,
        vhost=rabbitmq_vhost,
        exchange=rabbitmq_exchange,
        login_callback=perform_login,
    )

    # Start consuming messages
    try:
        subscriber.start_consuming()
    except KeyboardInterrupt:
        logger.info("Shutting down mini-fb-service...")
        subscriber.disconnect()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        subscriber.disconnect()


if __name__ == "__main__":
    main()
