"""
Command Handler - Manages and executes commands
"""

import threading
import concurrent.futures
from __sendMessage import api
from .uptime_command import UptimeCommand
from .hello_command import HelloCommand
from .ping_command import PingCommand
from .img_command import ImgCommand
from .lol_command import LolCommand
from .rank_command import RankCommand
from .analys_command import AnalysCommand
from .ask_command import AskCommand


class CommandHandler:
    """
    Handles command registration and execution with parallel processing support
    """
    
    def __init__(self, max_workers: int = 5):
        self.commands = []
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self._register_default_commands()
    
    def _register_default_commands(self):
        """Register all default commands"""
        self.register_command(UptimeCommand())
        self.register_command(HelloCommand())
        self.register_command(PingCommand())
        self.register_command(ImgCommand())
        self.register_command(LolCommand())
        self.register_command(RankCommand())
        self.register_command(AnalysCommand())
        self.register_command(AskCommand())
    
    def register_command(self, command):
        """
        Register a new command
        
        Args:
            command: An instance of a BaseCommand subclass
        """
        self.commands.append(command)
    
    def get_command(self, command_str: str):
        """
        Get the command that matches the given command string
        
        Args:
            command_str: The command string to match
        
        Returns:
            The matching command instance or None
        """
        for command in self.commands:
            if command.matches(command_str):
                return command
        return None
    
    def execute_command(self, client, dataFB, command_str: str):
        """
        Execute a command (synchronous)
        
        Args:
            client: The fbClient instance
            dataFB: Facebook data dictionary
            command_str: The command string to execute
        
        Returns:
            dict with keys:
            - bodySend: The message to send (optional)
            - attachmentID: Attachment ID (optional)
            - typeAttachment: Type of attachment (optional)
        """
        command = self.get_command(command_str)
        
        if command is None:
            return {
                "bodySend": None,
                "attachmentID": None,
                "typeAttachment": None
            }
        
        # Extract arguments from command string
        args = ""
        if command.name != command_str.lower():
            # For commands with arguments (lol, rank, analys)
            if command_str.lower().startswith(command.name.lower() + " "):
                args = command_str[len(command.name) + 1:]
        
        # Execute the command
        result = command.execute(client, dataFB, args)
        
        return result
    
    def execute_command_async(self, client, dataFB, command_str: str, reply_to_id: str, type_chat: str):
        """
        Execute a command asynchronously in a separate thread
        
        Args:
            client: The fbClient instance
            dataFB: Facebook data dictionary
            command_str: The command string to execute
            reply_to_id: The thread/user ID to reply to
            type_chat: The type of chat ('user' or 'thread')
        
        Returns:
            concurrent.futures.Future object
        """
        def _execute_and_send():
            # Execute the command
            result = self.execute_command(client, dataFB, command_str)
            
            # Send the response if there is one
            if result.get("bodySend") is not None:
                self.send_response(client, dataFB, result, reply_to_id, type_chat)
            
            return result
        
        # Submit to thread pool for parallel execution
        future = self.executor.submit(_execute_and_send)
        return future
    
    def shutdown(self, wait: bool = True):
        """
        Shutdown the executor, waiting for pending tasks to complete
        
        Args:
            wait: Whether to wait for pending tasks to complete
        """
        self.executor.shutdown(wait=wait)
    
    def send_response(self, client, dataFB, result: dict, reply_to_id: str = None, type_chat: str = None):
        """
        Send the response from a command execution
        
        Args:
            client: The fbClient instance
            dataFB: Facebook data dictionary
            result: The result dict from command execution
            reply_to_id: The thread/user ID to reply to (optional, defaults to client.replyToID)
            type_chat: The type of chat ('user' or 'thread', optional, defaults to client.typeChat)
        """
        if result.get("bodySend") is not None:
            # Use provided values or fall back to client values
            target_reply_to_id = reply_to_id if reply_to_id is not None else client.replyToID
            target_type_chat = type_chat if type_chat is not None else client.typeChat
            
            mainSend = api()
            threading.Thread(
                target=mainSend.send,
                args=(
                    dataFB,
                    result["bodySend"],
                    target_reply_to_id,
                    result.get("typeAttachment"),
                    result.get("attachmentID"),
                    target_type_chat
                )
            ).start()
    
    def list_commands(self) -> list:
        """
        Get a list of all registered commands
        
        Returns:
            List of command information dicts
        """
        return [
            {
                "name": cmd.name,
                "aliases": cmd.aliases,
                "description": cmd.description
            }
            for cmd in self.commands
        ]
