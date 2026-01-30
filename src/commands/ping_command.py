"""
Ping command - Simple pong response
"""

from .base_command import BaseCommand


class PingCommand(BaseCommand):
    """Command to respond with Pong!"""
    
    @property
    def name(self) -> str:
        return "ping"
    
    @property
    def description(self) -> str:
        return "Trả lời Pong!"
    
    def execute(self, client, dataFB, args: str = "") -> dict:
        return {
            "bodySend": "Pong!",
            "attachmentID": None,
            "typeAttachment": None
        }
