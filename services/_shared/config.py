"""
Shared configuration module for all services.
Uses environment variables for configuration with fallback to defaults.
"""

import os


# Proxy Configuration
# Format: http://username:password@proxy_host:port or http://proxy_host:port
# Leave empty to disable proxy
FACEBOOK_PROXY = os.getenv("FACEBOOK_PROXY", "")

# Riot Games API Key
# Get your API key from: https://developer.riotgames.com/
RIOT_API_KEY = os.getenv("RIOT_API_KEY", "")

# Google Gemini API Key
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# OpenAI API Key
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# AI Provider Selection
# Options: "gemini" or "openai"
# Default: "gemini"
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")

# OpenAI Configuration
# Base URL for OpenAI API (default: https://api.openai.com/v1)
# Can be changed to use OpenAI-compatible endpoints (e.g., local LLMs)
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

# OpenAI Model to use (default: gpt-4o-mini)
# Available models: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo, etc.
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Player Aliases - Maps alias names to Riot IDs (name#tag)
# Format: "Alias": "GameName#TagLine"
PLAYER_ALIASES = {
    "Khánh": "Em Khánh#AE34",
    "Hoàng": "TH TrueLove#nxh",
    "Lâm": "Đậu Phụ Rán Giòn#2002",
    "Huy": "Cu Đơ Hà Tĩnh#Wuy",
    "Vũ": "Cột Sống ko ổn#vn2",
    "Minh": "temp125hjk2jdka#7672",
}

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "10.0.8.0")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "admin123")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "fbchat.events")

# RabbitMQ Queue Names
QUEUE_MESSAGE_RECEIVED = "message.received"
QUEUE_MESSAGE_SEND = "message.send"
QUEUE_COOKIE_CHANGED = "cookie.changed"
QUEUE_MATCH_ENDED = "match.ended"
QUEUE_MESSENGER_DISCONNECTED = "messenger.disconnected"

# Facebook Configuration (fbchat-core)
FBCHAT_COOKIE = os.getenv("FBCHAT_COOKIE", "")

# Facebook Login Configuration (mini-fb-service)
MINIFB_ACCOUNT = os.getenv("MINIFB_ACCOUNT", "0382582262")
MINIFB_PASSWORD = os.getenv("MINIFB_PASSWORD", "hoangngu2002")
MINIFB_HEADLESS = os.getenv("MINIFB_HEADLESS", "false").lower() == "true"
MINIFB_CHROME_VERSION = os.getenv("MINIFB_CHROME_VERSION", None)
MINIFB_USER_DATA_DIR = os.getenv("MINIFB_USER_DATA_DIR", None)
MINIFB_PROXY = os.getenv("MINIFB_PROXY", None)
