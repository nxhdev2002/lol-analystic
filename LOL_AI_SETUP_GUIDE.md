# LOL AI Chat - Setup and Usage Guide

## Overview
The LOL AI Chat feature has been successfully integrated into your Facebook chat bot. When users send the command `/lol <playername>`, the bot will:
1. Fetch the last 5 match data for the player from Riot Games API
2. Analyze the data using Google Gemini AI (via direct API calls)
3. Return a detailed analysis in Vietnamese

## Files Created/Modified

### New Files Created:
- [`src/riot_api.py`](src/riot_api.py) - Riot Games API integration module
- [`src/gemini_ai.py`](src/gemini_ai.py) - Gemini AI integration module (using direct API calls)
- [`plans/lol-ai-integration-plan.md`](plans/lol-ai-integration-plan.md) - Detailed implementation plan

### Files Modified:
- [`src/main.py`](src/main.py) - Added LOL command handler and API keys

## Setup Instructions

### 1. Install Dependencies
The project only uses `requests` library which is already in your [`requirements.txt`](requirements.txt). No additional dependencies are needed.

### 2. Get API Keys

#### Riot Games API Key
1. Go to [Riot Games Developer Portal](https://developer.riotgames.com/)
2. Sign in or create an account
3. Go to "My Applications" and create a new application
4. Copy your API key

#### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 3. Configure API Keys

Open [`src/main.py`](src/main.py) and update the API keys if needed:

```python
# API Keys
RIOT_API_KEY = "YOUR_RIOT_API_KEY_HERE"  # Replace with your Riot Games API key
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # Replace with your Google Gemini API key
```

## Usage

### Command Format
```
/lol <playername>
```

### Examples
```
/lol Faker
/lol ShowMaker
/lol Chovy
```

### Response Format
The AI will return a detailed analysis in Vietnamese with the following sections:

1. **TỔNG QUAN HIỆU SUẤT** - Overall performance summary
2. **ĐIỂM MẠNH** - Key strengths
3. **ĐIỂM YẾU** - Weaknesses to address
4. **GỢI Ý CẢI THIỆN** - Suggestions for improvement
5. **MẪU HÀNH VI** - Patterns across matches

## Features

### Match Data Included
- KDA (Kills/Deaths/Assists)
- Champion played
- Win/Loss result
- Game duration and mode
- Position played
- Gold earned
- Damage dealt to champions
- Items built
- Team objectives (Baron, Dragon, Towers)

### Error Handling
The bot handles various error scenarios:
- Player not found
- No recent matches
- API rate limits
- Invalid API keys
- Network errors

## API Rate Limits

### Riot Games API
- Development key: 20 requests per second, 100 requests per 2 minutes
- Production key: Higher limits (requires approval)

### Google Gemini API
- Free tier: 15 requests per minute
- Paid tier: Higher limits

## Implementation Details

### Direct API Calls
The implementation uses direct HTTP requests to the Gemini API instead of the official library. This means:

- **No additional dependencies** - Only `requests` is needed
- **Full control** - Direct access to API parameters
- **Simpler setup** - No need to install Google's SDK

### Gemini API Endpoint
```
https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent
```

## Troubleshooting

### Common Issues

1. **"API key không hợp lệ hoặc đã hết hạn"**
   - Check if your API keys are correct
   - Ensure the keys haven't expired

2. **"Không tìm thấy người chơi"**
   - Verify the summoner name is spelled correctly
   - Check if the player is on the Vietnam server

3. **"Đã vượt quá giới hạn API"**
   - Wait for the rate limit to reset
   - Consider upgrading to a production API key

4. **"Lỗi kết nối"**
   - Check your internet connection
   - Verify the API endpoints are accessible

## Code Structure

### RiotAPI Class ([`src/riot_api.py`](src/riot_api.py))
```python
riot_api = RiotAPI(api_key)
match_data = riot_api.get_player_matches(player_name, count=5)
```

### GeminiAI Class ([`src/gemini_ai.py`](src/gemini_ai.py))
```python
gemini = GeminiAI(api_key)
analysis = gemini.analyze_lol_matches(match_data, player_name)
```

## API Reference

### Gemini API Request Format
```json
{
  "contents": [
    {
      "parts": [
        {
          "text": "Your prompt here"
        }
      ]
    }
  ],
  "generationConfig": {
    "temperature": 0.7,
    "topK": 40,
    "topP": 0.95,
    "maxOutputTokens": 8192
  }
}
```

### Gemini API Response Format
```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "Generated response here"
          }
        ]
      }
    }
  ]
}
```

## Future Enhancements

Possible improvements for future versions:
- Cache match data to reduce API calls
- Add more commands (e.g., `/lol stats`, `/lol rank`)
- Support multiple regions
- Add emoji reactions based on win/loss
- Support Vietnamese summoner names with special characters
- Add leaderboard comparison features

## Support

If you encounter any issues:
1. Check the error message for specific details
2. Verify your API keys are valid
3. Ensure you have internet connectivity
4. Check the API status pages:
   - [Riot Games API Status](https://developer.riotgames.com/status)
   - [Google AI Status](https://status.cloud.google.com/)
