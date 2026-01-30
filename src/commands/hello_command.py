"""
Hello command - Greeting command with multiple aliases
"""

from .base_command import BaseCommand


class HelloCommand(BaseCommand):
    """Command to greet users"""
    
    @property
    def name(self) -> str:
        return "hello"
    
    @property
    def aliases(self) -> list:
        return ["hola", "hi"]
    
    @property
    def description(self) -> str:
        return "Chào hỏi người dùng"
    
    def execute(self, client, dataFB, args: str = "") -> dict:
        return {
            "bodySend": "Hey, " + client.userID,
            "attachmentID": None,
            "typeAttachment": None
        }
