# mini-fb-service

Facebook automation service for automated login and cookie management.

## Responsibilities

- Automated Facebook login with undetected browser (Selenium + undetected_chromedriver)
- Extract cookie string in a consistent format
- Consume events:
  - `messenger.disconnected` - trigger relogin when fbchat-core reports disconnection
- Publish events:
  - `cookie.changed` - when cookie is refreshed or login is verified

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RABBITMQ_HOST` | RabbitMQ host | `localhost` |
| `RABBITMQ_PORT` | RabbitMQ port | `5672` |
| `RABBITMQ_USER` | RabbitMQ user | `guest` |
| `RABBITMQ_PASSWORD` | RabbitMQ password | `guest` |
| `RABBITMQ_VHOST` | RabbitMQ vhost | `/` |
| `RABBITMQ_EXCHANGE` | RabbitMQ exchange name | `fbchat.events` |
| `MINIFB_ACCOUNT` | Facebook account email/phone | - |
| `MINIFB_PASSWORD` | Facebook account password | - |
| `MINIFB_HEADLESS` | Run browser in headless mode | `true` |
| `MINIFB_CHROME_VERSION` | Force Chrome version for ChromeDriver (e.g., "144") | Auto-detected |
| `MINIFB_USER_DATA_DIR` | Chrome user data directory path for persistent session (reduces CAPTCHA) | None |
| `MINIFB_PROXY` | Proxy server URL (e.g., `http://proxy.example.com:8080` or `socks5://proxy.example.com:1080`) | None |

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python -m mini_fb_service.main
```

## Docker

```bash
# Build
docker build -t mini-fb-service .

# Run
docker run --env-file .env mini-fb-service
```

## Architecture

```
messenger.disconnected event
         |
         v
mini-fb-service receives event
         |
         v
Trigger automated login with undetected browser (Selenium + undetected_chromedriver)
         |
         v
Extract fresh cookie
         |
         v
Publish cookie.changed event
```

## Operational Notes

### Browser Configuration
- **Browser**: Uses Chrome/Chromium via `undetected_chromedriver` for anti-bot detection
- **Headless Mode**: Controlled by `MINIFB_HEADLESS` (default: `false`)
  - Headful mode is recommended for production to reduce CAPTCHA triggers
  - Headless mode (`MINIFB_HEADLESS=true`) is more resource-efficient but may increase CAPTCHA risk

### CAPTCHA and Security Checks
- **CAPTCHA**: `undetected_chromedriver` helps avoid detection but CAPTCHA may still occur
- **Checkpoint/2FA**: If Facebook requires additional verification (2FA, checkpoint, etc.), the login will fail and return `None`
  - Current implementation does not handle 2FA/checkpoint flows
  - Manual intervention may be required for accounts with 2FA enabled

### Troubleshooting
- **ChromeDriver version mismatch**: If you see "This version of ChromeDriver only supports Chrome version X" error:
  - Set `MINIFB_CHROME_VERSION` to your Chrome major version (e.g., `144`)
  - Check your Chrome version at `chrome://version`
- **Reduce CAPTCHA with proxy**:
  - Set `MINIFB_PROXY` to a proxy URL (e.g., `http://proxy.example.com:8080`)
  - Use residential proxies for better results (avoid datacenter IPs)
  - Proxy format: `http://user:pass@host:port` or `socks5://user:pass@host:port`
- **Reduce CAPTCHA with persistent session**:
  - Set `MINIFB_USER_DATA_DIR` to a path (e.g., `/app/chrome-profile` or `C:/Users/YourUser/chrome-profile`)
  - This saves cookies and session data between runs, making login look more natural
- **If login fails repeatedly**:
  - Try running in headful mode (`MINIFB_HEADLESS=false`)
  - Check logs for specific error messages and URL patterns (e.g., `checkpoint` in URL)
