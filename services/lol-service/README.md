# lol-service

League of Legends domain service for handling LoL-related features.

## Responsibilities

- LoL domain adapters: Riot API, match tracking, rank lookup
- Consumes `message.received` to detect LoL commands
- Publishes events:
  - `message.send` - to send responses back via fbchat-core
  - `match.ended` - when a match ends (optional, depends on responsibility split)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RABBITMQ_HOST` | RabbitMQ host | `localhost` |
| `RABBITMQ_PORT` | RabbitMQ port | `5672` |
| `RABBITMQ_USER` | RabbitMQ user | `guest` |
| `RABBITMQ_PASSWORD` | RabbitMQ password | `guest` |
| `RABBITMQ_VHOST` | RabbitMQ vhost | `/` |
| `RABBITMQ_EXCHANGE` | RabbitMQ exchange name | `fbchat.events` |
| `RIOT_API_KEY` | Riot Games API key | - |
| `AI_PROVIDER` | AI provider for responses (`gemini` or `openai`) | `gemini` |
| `GEMINI_API_KEY` | Google Gemini API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `OPENAI_BASE_URL` | OpenAI base URL | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | OpenAI model name | `gpt-4o-mini` |

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python -m lol_service.main
```

## Docker

```bash
# Build
docker build -t lol-service .

# Run
docker run --env-file .env lol-service
```
