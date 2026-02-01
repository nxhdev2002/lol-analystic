# fbchat-core

Facebook Messenger core service for receiving and sending messages.

## Responsibilities

- Facebook session/cookie management (consumes cookie updates)
- Messenger MQTT long-poll/listen for incoming messages
- Publish events:
  - `message.received` - when a message is received from Facebook
  - `messenger.disconnected` - when Messenger MQTT connection is lost
- Consume events:
  - `message.send` - to send outbound messages
  - `cookie.changed` - to update cookies and reconnect

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RABBITMQ_HOST` | RabbitMQ host | `localhost` |
| `RABBITMQ_PORT` | RabbitMQ port | `5672` |
| `RABBITMQ_USER` | RabbitMQ user | `guest` |
| `RABBITMQ_PASSWORD` | RabbitMQ password | `guest` |
| `RABBITMQ_VHOST` | RabbitMQ vhost | `/` |
| `RABBITMQ_EXCHANGE` | RabbitMQ exchange name | `fbchat.events` |
| `FBCHAT_COOKIE` | Initial Facebook cookie (optional if mini-fb-service provides) | - |
| `FACEBOOK_PROXY` | Proxy URL for Facebook requests | - |

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python -m fbchat_core.main
```

## Docker

```bash
# Build
docker build -t fbchat-core .

# Run
docker run --env-file .env fbchat-core
```
