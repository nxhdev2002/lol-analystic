"""
Configuration file for API keys
Centralized location for all API keys used in the application
"""

import os

# Proxy Configuration
# Format: http://username:password@proxy_host:port or http://proxy_host:port
# Example: http://proxy.example.com:8080 or http://user:pass@proxy.example.com:8080
# Leave empty to disable proxy
FACEBOOK_PROXY = os.getenv("FACEBOOK_PROXY", "")

# Riot Games API Key
# Get your API key from: https://developer.riotgames.com/
RIOT_API_KEY = "RGAPI-e2b581de-712b-4075-b0cc-7b2b25fe48a1"

# Google Gemini API Key
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY = "AIzaSyAxI_2zkq7hdh7VT8pWGtZvun3pCqdLpmk"

# OpenAI API Key
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY = "bot"

# AI Provider Selection
# Options: "gemini" or "openai"
# Default: "gemini"
AI_PROVIDER = "openai"

# OpenAI Configuration
# Base URL for OpenAI API (default: https://api.openai.com/v1)
# Can be changed to use OpenAI-compatible endpoints (e.g., local LLMs)
OPENAI_BASE_URL = "https://cli.hoangnx2002.io.vn/v1"

# OpenAI Model to use (default: gpt-4o-mini)
# Available models: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo, etc.
OPENAI_MODEL = "Grok Code Fast 1"

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
