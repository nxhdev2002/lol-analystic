"""
Uptime command - Shows current datetime
"""

import datetime
from .base_command import BaseCommand


class UptimeCommand(BaseCommand):
    """Command to show current datetime"""
    
    @property
    def name(self) -> str:
        return "uptime"
    
    @property
    def description(self) -> str:
        return "Hiển thị thời gian hiện tại"
    
    def execute(self, client, dataFB, args: str = "") -> dict:
        return {
            "bodySend": "datetime: " + str(datetime.datetime.now()),
            "attachmentID": None,
            "typeAttachment": None
        }
