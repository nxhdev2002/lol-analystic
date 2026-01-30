"""
Ask command - Ask AI a question about League of Legends player data
"""

import threading
import re
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


class AskCommand(BaseCommand):
    """Command to ask AI a question about League of Legends player data"""
    
    @property
    def name(self) -> str:
        return "ask"
    
    @property
    def description(self) -> str:
        return "Hỏi AI về dữ liệu người chơi League of Legends"
    
    def execute(self, client, dataFB, args: str = "") -> dict:
        params = args.strip()
        
        if not params:
            return {
                "bodySend": "Vui lòng nhập đúng định dạng: /ask tên#tag \"Câu hỏi cần hỏi AI\". Ví dụ: /ask tên#tag \"Tại sao tôi hay thua ở vị trí mid?\"",
                "attachmentID": None,
                "typeAttachment": None
            }
        
        try:
            # Parse the input: name#tag "question" or name#tag 'question'
            # Player names can contain spaces and special characters
            # Tag lines cannot contain spaces
            
            # Find the first quote (either " or ')
            first_quote_idx = -1
            quote_char = None
            for i, char in enumerate(params):
                if char in ['"', "'"]:
                    first_quote_idx = i
                    quote_char = char
                    break
            
            if first_quote_idx == -1:
                return {
                    "bodySend": "Vui lòng nhập câu hỏi trong ngoặc kép. Ví dụ: /ask tên#tag \"Câu hỏi cần hỏi AI\"",
                    "attachmentID": None,
                    "typeAttachment": None
                }
            
            # Find the matching closing quote
            closing_quote_idx = -1
            for i in range(first_quote_idx + 1, len(params)):
                if params[i] == quote_char:
                    closing_quote_idx = i
                    break
            
            if closing_quote_idx == -1:
                return {
                    "bodySend": "Vui lòng đóng ngoặc kép cho câu hỏi. Ví dụ: /ask tên#tag \"Câu hỏi cần hỏi AI\"",
                    "attachmentID": None,
                    "typeAttachment": None
                }
            
            # Extract player info and question
            player_info = params[:first_quote_idx].strip()
            question = params[first_quote_idx + 1:closing_quote_idx].strip()
            
            # Resolve player alias if provided
            resolved_player_info = resolve_player_alias(player_info)
            
            # Validate player info format
            if "#" not in resolved_player_info:
                return {
                    "bodySend": "Không tìm thấy alias hoặc định dạng không đúng. Vui lòng nhập tên người chơi#tag hoặc alias. Ví dụ: /ask tên#tag \"Câu hỏi\" hoặc /ask Khánh \"Câu hỏi\"",
                    "attachmentID": None,
                    "typeAttachment": None
                }
            
            # Split name and tag
            parts = resolved_player_info.split("#", 1)
            game_name = parts[0].strip()
            tag_line = parts[1].strip()
            
            # Validate question is not empty
            if not question:
                return {
                    "bodySend": "Vui lòng nhập câu hỏi cần hỏi AI. Ví dụ: /ask tên#tag \"Tại sao tôi hay thua ở vị trí mid?\"",
                    "attachmentID": None,
                    "typeAttachment": None
                }
            
            player_display = f"{game_name}#{tag_line}"
            
            # Show alias if used
            display_info = f"{player_info} ({player_display})" if player_info != resolved_player_info else player_display
            
            # Send processing message
            processing_msg = f"Đang lấy dữ liệu và phân tích cho {display_info}..."
            mainSend = api()
            threading.Thread(
                target=mainSend.send,
                args=(dataFB, processing_msg, client.replyToID, None, None, client.typeChat)
            ).start()
            
            # Fetch rank data from Riot API
            riot_api = RiotAPI(RIOT_API_KEY)
            rank_data = riot_api.get_player_rank(game_name, tag_line)
            
            # Fetch 5 recent ranked matches from Riot API
            ranked_data = riot_api.get_ranked_matches_by_riot_id(game_name, tag_line, count=5)
            
            # Analyze with AI
            ai_client = get_ai_client()
            result = ai_client.ask_lol_question(rank_data, ranked_data, player_display, question)
            
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
        """Check if the given command matches this command (starts with 'ask ')"""
        return command.lower().startswith("ask ")
