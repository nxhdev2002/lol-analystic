"""
Match publisher for OnMatchEnd event.
Publishes match completion events from Riot API to RabbitMQ.
"""

import logging
from typing import Optional, Dict, Any

from rabbitmq_client import BasePublisher, RabbitMQConnection
from config import QUEUE_MATCH_ENDED
from events import MatchEndedEvent

logger = logging.getLogger(__name__)


class MatchPublisher(BasePublisher):
    """
    Publisher for MatchEnded events.
    Publishes match completion events from Riot API to RabbitMQ.
    """

    def __init__(self, connection: Optional[RabbitMQConnection] = None):
        """
        Initialize the match publisher.
        
        Args:
            connection: RabbitMQ connection instance. If None, creates a new one.
        """
        if connection is None:
            connection = RabbitMQConnection()
        super().__init__(connection)

    def publish_match_ended(
        self,
        match_id: str,
        puuid: str,
        summoner_name: str,
        game_duration: int,
        win: bool,
        champion: str,
        kills: int = 0,
        deaths: int = 0,
        assists: int = 0,
        kda: float = 0.0,
    ) -> bool:
        """
        Publish a MatchEnded event.
        
        Args:
            match_id: Riot match ID
            puuid: Player PUUID
            summoner_name: Summoner name
            game_duration: Game duration in seconds
            win: True if player won the match
            champion: Champion played
            kills: Number of kills
            deaths: Number of deaths
            assists: Number of assists
            kda: KDA ratio
            
        Returns:
            True if published successfully, False otherwise
        """
        try:
            # Create event using Pydantic model
            event = MatchEndedEvent(
                event_type="match.ended",
                data={
                    "match_id": match_id,
                    "puuid": puuid,
                    "summoner_name": summoner_name,
                    "game_duration": game_duration,
                    "win": win,
                    "champion": champion,
                    "kills": kills,
                    "deaths": deaths,
                    "assists": assists,
                    "kda": kda,
                }
            )
            
            # Convert to dict for publishing
            event_dict = event.model_dump()
            
            # Publish to RabbitMQ
            return self.publish(
                routing_key=QUEUE_MATCH_ENDED,
                event=event_dict
            )
        except Exception as e:
            logger.error(f"Failed to publish MatchEnded event: {e}")
            return False

    def publish_from_dict(self, match_data: Dict[str, Any]) -> bool:
        """
        Publish a MatchEnded event from a dictionary.
        
        Args:
            match_data: Dictionary containing match data with keys:
                - match_id
                - puuid
                - summoner_name
                - game_duration
                - win
                - champion
                - kills (optional)
                - deaths (optional)
                - assists (optional)
                - kda (optional)
                
        Returns:
            True if published successfully, False otherwise
        """
        try:
            return self.publish_match_ended(
                match_id=match_data.get("match_id", ""),
                puuid=match_data.get("puuid", ""),
                summoner_name=match_data.get("summoner_name", ""),
                game_duration=match_data.get("game_duration", 0),
                win=match_data.get("win", False),
                champion=match_data.get("champion", ""),
                kills=match_data.get("kills", 0),
                deaths=match_data.get("deaths", 0),
                assists=match_data.get("assists", 0),
                kda=match_data.get("kda", 0.0),
            )
        except Exception as e:
            logger.error(f"Failed to publish match from dict: {e}")
            return False
