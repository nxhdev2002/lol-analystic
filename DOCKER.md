# Docker Guide for fbchat-v2

This guide explains how to build and run the fbchat-v2 project using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, for easier management)

## Quick Start

### 1. Configure Environment Variables

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your actual API keys:
- `RIOT_API_KEY` - Get from https://developer.riotgames.com/
- `GEMINI_API_KEY` - Get from https://makersuite.google.com/app/apikey
- `OPENAI_API_KEY` - Get from https://platform.openai.com/api-keys

### 2. Build and Run with Docker Compose (Recommended)

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

### 3. Build and Run with Docker CLI

```bash
# Build the image
docker build -t fbchat-bot .

# Run the container
docker run -d \
  --name fbchat-bot \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  fbchat-bot

# View logs
docker logs -f fbchat-bot

# Stop the container
docker stop fbchat-bot
docker rm fbchat-bot
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RIOT_API_KEY` | Riot Games API key for League of Legends features | (empty) |
| `GEMINI_API_KEY` | Google Gemini API key for AI features | (empty) |
| `OPENAI_API_KEY` | OpenAI API key for AI features | (empty) |
| `AI_PROVIDER` | AI provider to use: `gemini` or `openai` | `gemini` |
| `OPENAI_BASE_URL` | Base URL for OpenAI API | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4o-mini` |

## Volume Mounts

- `/app/logs` - Container logs directory (mounted to `./logs` on host)

## Troubleshooting

### Container exits immediately

Check the logs:
```bash
docker logs fbchat-bot
```

### Rebuild after code changes

```bash
docker-compose up -d --build
```

### Clean up everything

```bash
docker-compose down -v
docker system prune -a
```

## Development

For development, you may want to mount the source code directory:

```bash
docker run -d \
  --name fbchat-bot \
  --env-file .env \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/language:/app/language \
  -v $(pwd)/logs:/app/logs \
  fbchat-bot
```

This allows you to make changes to the code without rebuilding the image.
