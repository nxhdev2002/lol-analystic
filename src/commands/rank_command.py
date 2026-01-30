"""
Rank command - Get League of Legends player rank
"""

import threading
from .base_command import BaseCommand
from riot_api import RiotAPI
from gemini_ai import GeminiAI
from openai_ai import OpenAIAI
from __sendMessage import api
from config import (
    RIOT_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY,
    AI_PROVIDER, OPENAI_BASE_URL, OPENAI_MODEL, PLAYER_ALIASES
)


def get_ai_client():
    """
    Get the appropriate AI client based on the AI_PROVIDER setting.
    
    Returns:
        GeminiAI or OpenAIAI: The AI client instance
    """
    if AI_PROVIDER.lower() == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in config.py or switch to Gemini.")
        return OpenAIAI(OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL)
    else:
        if not GEMINI_API_KEY:
            raise ValueError("Gemini API key not configured. Please set GEMINI_API_KEY in config.py or switch to OpenAI.")
        return GeminiAI(GEMINI_API_KEY)


def resolve_player_alias(player_info: str) -> str:
    """
    Resolve player alias to Riot ID.
    
    Args:
        player_info (str): The player info (alias or name#tag)
        
    Returns:
        str: The resolved Riot ID (name#tag)
    """
    player_info = player_info.strip()
    
    # If it's already a Riot ID (contains #), return as is
    if "#" in player_info:
        return player_info
    
    # Check if it's an alias (case-insensitive)
    for alias, riot_id in PLAYER_ALIASES.items():
        if alias.lower() == player_info.lower():
            return riot_id
    
    # Not an alias, return original
    return player_info


class RankCommand(BaseCommand):
    """Command to get League of Legends player rank"""
    
    @property
    def name(self) -> str:
        return "rank"
    
    @property
    def description(self) -> str:
        return "Lấy thông tin xếp hạng League of Legends"
    
    def execute(self, client, dataFB, args: str = "") -> dict:
        player_info = args.strip()
        
        if not player_info:
            return {
                "bodySend": "Vui lòng nhập tên người chơi và tag hoặc alias. Ví dụ: /rank tên#tag hoặc /rank Khánh",
                "attachmentID": None,
                "typeAttachment": None
            }
        
        try:
            # Resolve player alias if provided
            resolved_player_info = resolve_player_alias(player_info)
            
            # Validate player info format
            if "#" not in resolved_player_info:
                return {
                    "bodySend": "Không tìm thấy alias hoặc định dạng không đúng. Vui lòng nhập tên người chơi#tag hoặc alias. Ví dụ: /rank tên#tag hoặc /rank Khánh",
                    "attachmentID": None,
                    "typeAttachment": None
                }
            
            # Split name and tag
            parts = resolved_player_info.split("#", 1)
            game_name = parts[0].strip()
            tag_line = parts[1].strip()
            
            player_display = f"{game_name}#{tag_line}"
            
            # Show alias if used
            display_info = f"{player_info} ({player_display})" if player_info != resolved_player_info else player_display
            
            # Send processing message
            processing_msg = f"Đang lấy thông tin xếp hạng của {display_info}... Vui lòng đợi!"
            mainSend = api()
            threading.Thread(
                target=mainSend.send,
                args=(dataFB, processing_msg, client.replyToID, None, None, client.typeChat)
            ).start()
            
            # Fetch rank data from Riot API
            riot_api = RiotAPI(RIOT_API_KEY)
            rank_data = riot_api.get_player_rank(game_name, tag_line)
            
            # Update player display for AI analysis
            rank_data["game_name"] = game_name
            rank_data["tag_line"] = tag_line
            
            # Analyze with AI
            ai_client = get_ai_client()
            result = ai_client.analyze_lol_rank(rank_data)
            
            return {
                "bodySend": result,
                "attachmentID": None,
                "typeAttachment": None
            }
            
        except ValueError as e:
            return {
                "bodySend": f"Lỗi: {str(e)}",
                "attachmentID": None,
                "typeAttachment": None
            }
        except Exception as e:
            return {
                "bodySend": f"Có lỗi xảy ra: {str(e)}",
                "attachmentID": None,
                "typeAttachment": None
            }
    
    def matches(self, command: str) -> bool:
        """Check if the given command matches this command (starts with 'rank ')"""
        return command.lower().startswith("rank ")
