# Infrastructure

This directory contains Docker Compose configuration for running the fbchat microservices architecture.

## Services

| Service | Description | Ports |
|---------|-------------|--------|
| `rabbitmq` | RabbitMQ message broker with management UI | 5672 (AMQP), 15672 (Management) |
| `fbchat-core` | Facebook Messenger core service | - |
| `lol-service` | League of Legends domain service | - |
| `mini-fb-service` | Facebook automation service | - |

## Quick Start

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## Environment Variables

See [`.env.example`](.env.example) for all available environment variables.

## Development

For local development with source code mounting, create a `docker-compose.override.yml`:

```yaml
version: '3.8'

services:
  fbchat-core:
    volumes:
      - ../services/fbchat-core/src:/app/src

  lol-service:
    volumes:
      - ../services/lol-service/src:/app/src

  mini-fb-service:
    volumes:
      - ../services/mini-fb-service/src:/app/src
```

## RabbitMQ Management UI

Access the RabbitMQ management UI at http://localhost:15672

- Username: `guest`
- Password: `guest`

## Event Flow

```
fbchat-core --[message.received]--> RabbitMQ --[message.received]--> lol-service
lol-service --[message.send]--> RabbitMQ --[message.send]--> fbchat-core

fbchat-core --[messenger.disconnected]--> RabbitMQ --[messenger.disconnected]--> mini-fb-service
mini-fb-service --[cookie.changed]--> RabbitMQ --[cookie.changed]--> fbchat-core
```

## Troubleshooting

### View logs for a specific service

```bash
docker-compose logs -f fbchat-core
docker-compose logs -f lol-service
docker-compose logs -f mini-fb-service
```

### Rebuild a specific service

```bash
docker-compose up -d --build fbchat-core
```

### Restart all services

```bash
docker-compose restart
```

### Clean up everything

```bash
docker-compose down -v
```
