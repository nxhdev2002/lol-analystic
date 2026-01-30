"""
LOL command - Analyze League of Legends matches
"""

import threading
from .base_command import BaseCommand
from riot_api import RiotAPI
from gemini_ai import GeminiAI
from __sendMessage import api
from config import RIOT_API_KEY, GEMINI_API_KEY


class LolCommand(BaseCommand):
    """Command to analyze League of Legends matches"""
    
    @property
    def name(self) -> str:
        return "lol"
    
    @property
    def description(self) -> str:
        return "Phân tích trận đấu League of Legends"
    
    def execute(self, client, dataFB, args: str = "") -> dict:
        player_name = args.strip()
        
        if not player_name:
            return {
                "bodySend": "Vui lòng nhập tên người chơi. Ví dụ: /lol playername",
                "attachmentID": None,
                "typeAttachment": None
            }
        
        try:
            # Send processing message
            processing_msg = f"Đang phân tích trận đấu của {player_name}... Vui lòng đợi!"
            mainSend = api()
            threading.Thread(
                target=mainSend.send,
                args=(dataFB, processing_msg, client.replyToID, None, None, client.typeChat)
            ).start()
            
            # Fetch match data from Riot API
            riot_api = RiotAPI(RIOT_API_KEY)
            match_data = riot_api.get_player_matches(player_name, count=5)
            
            # Check if matches were found
            if not match_data.get("matches"):
                return {
                    "bodySend": f"Không tìm thấy trận đấu nào gần đây cho người chơi '{player_name}'",
                    "attachmentID": None,
                    "typeAttachment": None
                }
            
            # Analyze with Gemini AI
            gemini = GeminiAI(GEMINI_API_KEY)
            result = gemini.analyze_lol_matches(match_data, player_name)
            
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
        """Check if the given command matches this command (starts with 'lol ')"""
        return command.lower().startswith("lol ")
