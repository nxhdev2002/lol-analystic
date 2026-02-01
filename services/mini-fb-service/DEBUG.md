# Debug mini-fb-service

## Debug Multiple Services Together

Bạn có thể debug **cả fbchat-core và mini-fb-service cùng lúc**:

1. Mở VSCode, nhấn F5 hoặc chọn "Debug Core + MiniFB (both)"
2. VSCode sẽ mở 2 terminal và debug cả 2 service
3. Đặt breakpoint ở bất kỳ đâu trong cả 2 service

Hoặc chọn "Debug Core + MiniFB + RabbitMQ" để tự động start RabbitMQ trước.

## Overview

This guide explains how to debug mini-fb-service in the microservices architecture.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Local Machine                                          │
│  ┌─────────────────┐    ┌──────────────────────────┐   │
│  │ VSCode Debugger │───▶│ mini-fb-service (local)  │   │
│  │ (breakpoints)   │    │ PYTHONPATH configured    │   │
│  └─────────────────┘    └───────────┬──────────────┘   │
│                                     │ AMQP             │
├─────────────────────────────────────┼───────────────────┤
│  Docker                             ▼                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │ RabbitMQ (docker-compose up rabbitmq -d)         │  │
│  │ localhost:5672                                   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Running the Service

### Option 1: Command Line

```powershell
# From project root
cd d:\Projects\fbchat

# Run the service directly (PYTHONPATH is set automatically)
python services/mini-fb-service/src/mini_fb_service/main.py

# Or using module execution (requires PYTHONPATH)
$env:PYTHONPATH = "services/mini-fb-service/src;services/_shared"; python -m mini_fb_service.main
```

### Option 2: VSCode Debug

1. Open VSCode
2. Press `F5` or go to Run and Debug
3. Select "Debug mini-fb-service"
4. Set breakpoints in:
   - `services/mini-fb-service/src/mini_fb_service/main.py`
   - `services/mini-fb-service/src/mini_fb_service/browser.py`
   - `services/mini-fb-service/src/mini_fb_service/subscriber.py`

## Running Dependencies

```powershell
# Start RabbitMQ only
cd infra
docker-compose up rabbitmq -d

# Or start all services
docker-compose up -d
```

## Running Tests

```powershell
# Run all tests
$env:PYTHONPATH = "services/mini-fb-service/src;services/_shared;src"
pytest services/mini-fb-service/tests/ -v

# Run specific test file
pytest services/mini-fb-service/tests/test_publisher.py -v -s

# Debug tests in VSCode
# Select "Debug mini-fb-service tests" from launch configuration
```

## Environment Variables

Required for debugging:

| Variable | Description | Default |
|----------|-------------|---------|
| `RABBITMQ_HOST` | RabbitMQ host | `localhost` |
| `RABBITMQ_PORT` | RabbitMQ port | `5672` |
| `RABBITMQ_USER` | RabbitMQ user | `guest` |
| `RABBITMQ_PASSWORD` | RabbitMQ password | `guest` |
| `MINIFB_ACCOUNT` | Facebook email | (required) |
| `MINIFB_PASSWORD` | Facebook password | (required) |
| `MINIFB_HEADLESS` | Run browser headless | `true` |
| `MINIFB_BROWSER_TYPE` | Browser type | `chromium` |

## Troubleshooting

### ModuleNotFoundError

If you see `No module named 'browser'` or similar:

1. Ensure PYTHONPATH is set correctly
2. Run from project root, not from service directory

### RabbitMQ Connection Failed

1. Ensure RabbitMQ is running: `docker ps`
2. Check connection settings in `services/_shared/config.py`
3. Verify RabbitMQ is accessible: `docker logs rabbitmq`

### Browser Automation Issues

1. Ensure Playwright is installed: `playwright install`
2. Check `MINIFB_HEADLESS` setting (set to `false` to see browser)
3. Verify Facebook credentials are correct

## Hot Reload

For development with hot reload, you can use:

```powershell
pip install watchdog
watchmedo auto-restart --directory=./services/mini-fb-service/src --pattern=*.py --recursive -- python -m mini_fb_service.main
```
