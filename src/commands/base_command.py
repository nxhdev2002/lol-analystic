"""
Base command class that all commands should inherit from
"""

from abc import ABC, abstractmethod


class BaseCommand(ABC):
    """
    Abstract base class for all commands
    
    Each command must implement:
    - name: The command name (without prefix)
    - aliases: Alternative names for the command
    - description: Description of what the command does
    - execute: The method that executes the command logic
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the primary command name"""
        pass
    
    @property
    def aliases(self) -> list:
        """Return list of alternative command names"""
        return []
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return command description"""
        pass
    
    @abstractmethod
    def execute(self, client, dataFB, args: str = "") -> dict:
        """
        Execute the command
        
        Args:
            client: The fbClient instance
            dataFB: Facebook data dictionary
            args: Command arguments (everything after the command name)
        
        Returns:
            dict with keys:
            - bodySend: The message to send (optional)
            - attachmentID: Attachment ID (optional)
            - typeAttachment: Type of attachment (optional)
        """
        pass
    
    def get_command_names(self) -> list:
        """Return all names that can trigger this command (name + aliases)"""
        return [self.name] + self.aliases
    
    def matches(self, command: str) -> bool:
        """Check if the given command matches this command"""
        return command.lower() in [name.lower() for name in self.get_command_names()]
