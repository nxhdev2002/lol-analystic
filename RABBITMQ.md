# RabbitMQ Integration Guide

This document provides information about the RabbitMQ integration in the fbchat project.

## Overview

The fbchat project now integrates with RabbitMQ for event-driven architecture. This allows decoupled communication between different components of the system.

## Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Facebook      │      │    RabbitMQ     │      │   Services      │
│   Messenger     │──────▶│   (Exchange)    │◀─────│   (Consumers)   │
└─────────────────┘      └─────────────────┘      └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
    Publishers              Queues & Routing Keys
```

## Events

### 1. OnMessageReceived (Publisher)

**Purpose**: Publishes received Facebook messages to RabbitMQ.

**Queue**: `message.received`

**Usage in main.py**:
```python
from publishers import MessagePublisher

# The MessagePublisher is automatically initialized in fbClient
# Messages are published when received from Facebook
```

**Event Structure**:
```json
{
  "event_type": "message.received",
  "timestamp": "2024-01-31T12:00:00Z",
  "data": {
    "message_id": "msg_123456",
    "user_id": "100014184491456",
    "sender_id": "100014184491456",
    "body": "Hello world",
    "reply_to_id": "thread_789",
    "type": "thread",
    "attachments": []
  }
}
```

### 2. OnMessageSendReceived (Subscriber)

**Purpose**: Consumes messages from RabbitMQ to send to Facebook Messenger.

**Queue**: `message.send`

**Usage**:
```python
from subscribers import MessageSendSubscriber
from rabbitmq_client import RabbitMQConnection

def send_callback(event):
    # Process the event and send message to Facebook
    print(f"Sending message: {event}")
    # TODO: Implement actual Facebook message sending

connection = RabbitMQConnection()
subscriber = MessageSendSubscriber(connection, send_callback)
subscriber.start()
```

**Event Structure**:
```json
{
  "event_type": "message.send",
  "timestamp": "2024-01-31T12:00:00Z",
  "data": {
    "recipient_id": "100014184491456",
    "recipient_type": "user",
    "body": "Reply message",
    "attachment_id": null,
    "attachment_type": null
  }
}
```

### 3. OnCookieChanged (Subscriber)

**Purpose**: Handles cookie change events and re-establishes Facebook connections.

**Queue**: `cookie.changed`

**Usage**:
```python
from subscribers import CookieChangeSubscriber
from rabbitmq_client import RabbitMQConnection

def reconnect_callback(event):
    # Process cookie change and reconnect to Facebook
    print(f"Cookie changed: {event}")
    # TODO: Implement actual Facebook reconnection

connection = RabbitMQConnection()
subscriber = CookieChangeSubscriber(connection, reconnect_callback)
subscriber.start()
```

**Event Structure**:
```json
{
  "event_type": "cookie.changed",
  "timestamp": "2024-01-31T12:00:00Z",
  "data": {
    "account_id": "100014184491456",
    "old_cookie": "...",
    "new_cookie": "...",
    "force_reconnect": true
  }
}
```

### 4. OnMatchEnd (Publisher)

**Purpose**: Publishes match completion events from Riot API to RabbitMQ.

**Queue**: `match.ended`

**Usage in riot_api.py**:
```python
from riot_api import RiotAPI

api = RiotAPI(api_key="your_api_key")

# Get and publish last match
match_data = api.get_and_publish_last_match(
    summoner_name="PlayerName",
    enable_rabbitmq=True
)

# Or publish match event directly
api.publish_match_event(
    match_id="VN2_1234567890",
    puuid="abc123",
    summoner_name="PlayerName",
    game_duration=1800,
    win=True,
    champion="Ahri",
    kills=10,
    deaths=3,
    assists=8,
    kda=6.0,
    enable_rabbitmq=True
)
```

**Event Structure**:
```json
{
  "event_type": "match.ended",
  "timestamp": "2024-01-31T12:00:00Z",
  "data": {
    "match_id": "VN2_1234567890",
    "puuid": "abc123-def456-ghi789",
    "summoner_name": "PlayerName",
    "game_duration": 1800,
    "win": true,
    "champion": "Ahri",
    "kills": 10,
    "deaths": 3,
    "assists": 8,
    "kda": 6.0
  }
}
```

## Configuration

### Environment Variables

Add these variables to your `.env` file:

```bash
# RabbitMQ Configuration
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/
RABBITMQ_EXCHANGE=fbchat.events
```

### Docker Compose

The RabbitMQ service is included in `docker-compose.yml`:

```yaml
services:
  rabbitmq:
    image: rabbitmq:3.12-management
    container_name: fbchat-rabbitmq
    restart: unless-stopped
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      - RABBITMQ_DEFAULT_USER=guest
      - RABBITMQ_DEFAULT_PASS=guest
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Running with Docker

1. Start the services:
```bash
docker-compose up -d
```

2. Access RabbitMQ Management UI:
```
http://localhost:15672
Username: guest
Password: guest
```

## File Structure

```
src/
├── rabbitmq_client.py       # Connection & base classes
├── events.py                # Pydantic event models
├── publishers/
│   ├── __init__.py
│   ├── message_publisher.py # Message received publisher
│   └── match_publisher.py  # Match ended publisher
└── subscribers/
    ├── __init__.py
    ├── message_send_subscriber.py
    └── cookie_change_subscriber.py
```

## Error Handling

The RabbitMQ client includes automatic reconnection logic with exponential backoff:

- Initial reconnection delay: 5 seconds
- Maximum reconnection delay: 60 seconds
- Automatic retry on connection failures

## Troubleshooting

### Connection Issues

If you see connection errors:

1. Check if RabbitMQ is running:
```bash
docker-compose ps
```

2. Check RabbitMQ logs:
```bash
docker-compose logs rabbitmq
```

3. Verify environment variables in `.env` file

### Message Not Published

1. Check if the exchange exists in RabbitMQ Management UI
2. Verify the routing key matches the queue binding
3. Check application logs for errors

### Subscriber Not Receiving Messages

1. Verify the queue is bound to the exchange with correct routing key
2. Check if messages are being acknowledged properly
3. Ensure the callback function doesn't raise exceptions

## Dependencies

- `pika>=1.3.2` - RabbitMQ Python client
- `pydantic>=2.0.0` - Event schema validation

## Future Extensions

Potential additional events:
- `on.typing.indicator` - User typing indicator
- `on.message.read` - Message read receipt
- `on.friend.request` - Friend request received
- `on.thread.info.changed` - Thread information changed
- `on.user.online` - User online status changed
