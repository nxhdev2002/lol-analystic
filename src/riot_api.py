"""
Riot Games API Integration Module
Handles all communications with Riot Games API for League of Legends data.
"""

import requests
import time
from typing import Optional


class RiotAPI:
    """Class to interact with Riot Games API for League of Legends data."""
    
    def __init__(self, api_key):
        """
        Initialize Riot API client.
        
        Args:
            api_key (str): Riot Games API key
        """
        self.api_key = api_key
        # Vietnam server endpoints
        self.base_url_vn = "https://vn2.api.riotgames.com"
        # Southeast Asia server endpoints (for match data)
        self.base_url_sea = "https://sea.api.riotgames.com"
        # Asia server endpoints (for account data)
        self.base_url_asia = "https://asia.api.riotgames.com"
        self.headers = {
            "X-Riot-Token": self.api_key
        }
    
    def get_puuid_by_name(self, summoner_name):
        """
        Get player PUUID by summoner name.
        
        Args:
            summoner_name (str): The summoner name to look up
            
        Returns:
            str: The player's PUUID
            
        Raises:
            ValueError: If player not found or API error occurs
        """
        url = f"{self.base_url_vn}/lol/summoner/v4/summoners/by-name/{summoner_name}"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 404:
                raise ValueError(f"Không tìm thấy người chơi '{summoner_name}'")
            elif response.status_code == 403:
                raise ValueError("API key không hợp lệ hoặc đã hết hạn")
            elif response.status_code == 429:
                retry_after = response.headers.get('Retry-After', 60)
                raise ValueError(f"Đã vượt quá giới hạn API. Vui lòng thử lại sau {retry_after} giây")
            elif response.status_code != 200:
                raise ValueError(f"Lỗi API: {response.status_code} - {response.text}")
            
            data = response.json()
            return data.get('puuid')
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Lỗi kết nối: {str(e)}")
    
    def get_match_ids_by_puuid(self, puuid, count=5):
        """
        Get last N match IDs by PUUID.
        
        Args:
            puuid (str): The player's PUUID
            count (int): Number of matches to retrieve (default: 5)
            
        Returns:
            list: List of match IDs
            
        Raises:
            ValueError: If API error occurs
        """
        url = f"{self.base_url_sea}/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params = {
            "start": 0,
            "count": count
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 404:
                raise ValueError("Không tìm thấy trận đấu nào cho người chơi này")
            elif response.status_code == 403:
                raise ValueError("API key không hợp lệ hoặc đã hết hạn")
            elif response.status_code == 429:
                retry_after = response.headers.get('Retry-After', 60)
                raise ValueError(f"Đã vượt quá giới hạn API. Vui lòng thử lại sau {retry_after} giây")
            elif response.status_code != 200:
                raise ValueError(f"Lỗi API: {response.status_code} - {response.text}")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Lỗi kết nối: {str(e)}")
    
    def get_match_details(self, match_id):
        """
        Get full match details including participants and timeline.
        
        Args:
            match_id (str): The match ID to retrieve
            
        Returns:
            dict: Full match details
            
        Raises:
            ValueError: If API error occurs
        """
        url = f"{self.base_url_sea}/lol/match/v5/matches/{match_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 404:
                raise ValueError(f"Không tìm thấy trận đấu {match_id}")
            elif response.status_code == 403:
                raise ValueError("API key không hợp lệ hoặc đã hết hạn")
            elif response.status_code == 429:
                retry_after = response.headers.get('Retry-After', 60)
                raise ValueError(f"Đã vượt quá giới hạn API. Vui lòng thử lại sau {retry_after} giây")
            elif response.status_code != 200:
                raise ValueError(f"Lỗi API: {response.status_code} - {response.text}")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Lỗi kết nối: {str(e)}")
    
    def get_puuid_by_riot_id(self, game_name, tag_line):
        """
        Get player PUUID by Riot ID (gameName#tagLine).
        
        Args:
            game_name (str): The game name (part before #)
            tag_line (str): The tag line (part after #)
            
        Returns:
            str: The player's PUUID
            
        Raises:
            ValueError: If player not found or API error occurs
        """
        url = f"{self.base_url_asia}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 404:
                raise ValueError(f"Không tìm thấy người chơi '{game_name}#{tag_line}'")
            elif response.status_code == 403:
                raise ValueError("API key không hợp lệ hoặc đã hết hạn")
            elif response.status_code == 429:
                retry_after = response.headers.get('Retry-After', 60)
                raise ValueError(f"Đã vượt quá giới hạn API. Vui lòng thử lại sau {retry_after} giây")
            elif response.status_code != 200:
                raise ValueError(f"Lỗi API: {response.status_code} - {response.text}")
            
            data = response.json()
            return data.get('puuid')
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Lỗi kết nối: {str(e)}")
    
    def get_league_entries_by_puuid(self, puuid):
        """
        Get league entries (rank data) by PUUID.
        
        Args:
            puuid (str): The player's PUUID
            
        Returns:
            list: List of league entries (solo/duo, flex, etc.)
            
        Raises:
            ValueError: If API error occurs
        """
        url = f"{self.base_url_vn}/lol/league/v4/entries/by-puuid/{puuid}"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 403:
                raise ValueError("API key không hợp lệ hoặc đã hết hạn")
            elif response.status_code == 429:
                retry_after = response.headers.get('Retry-After', 60)
                raise ValueError(f"Đã vượt quá giới hạn API. Vui lòng thử lại sau {retry_after} giây")
            elif response.status_code != 200:
                raise ValueError(f"Lỗi API: {response.status_code} - {response.text}")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Lỗi kết nối: {str(e)}")
    
    def get_player_rank(self, game_name, tag_line):
        """
        Convenience method to get rank data for a player by Riot ID.
        
        Args:
            game_name (str): The game name (part before #)
            tag_line (str): The tag line (part after #)
            
        Returns:
            dict: Dictionary containing player info and rank data
                {
                    "game_name": str,
                    "tag_line": str,
                    "puuid": str,
                    "league_entries": list
                }
            
        Raises:
            ValueError: If any error occurs during API calls
        """
        # Get PUUID by Riot ID
        puuid = self.get_puuid_by_riot_id(game_name, tag_line)
        
        # Get league entries
        league_entries = self.get_league_entries_by_puuid(puuid)
        
        return {
            "game_name": game_name,
            "tag_line": tag_line,
            "puuid": puuid,
            "league_entries": league_entries
        }
    
    def get_ranked_matches_by_riot_id(self, game_name, tag_line, count=5):
        """
        Get ranked match data for a player by Riot ID.
        
        Args:
            game_name (str): The game name (part before #)
            tag_line (str): The tag line (part after #)
            count (int): Number of ranked matches to retrieve (default: 5)
            
        Returns:
            dict: Dictionary containing player info and ranked match details
                {
                    "game_name": str,
                    "tag_line": str,
                    "puuid": str,
                    "matches": [
                        {
                            "match_id": str,
                            "match_data": dict
                        },
                        ...
                    ]
                }
            
        Raises:
            ValueError: If any error occurs during API calls
        """
        # Get PUUID by Riot ID
        puuid = self.get_puuid_by_riot_id(game_name, tag_line)
        
        # Get match IDs (get more to filter for ranked)
        match_ids = self.get_match_ids_by_puuid(puuid, count * 2)
        
        if not match_ids:
            return {
                "game_name": game_name,
                "tag_line": tag_line,
                "puuid": puuid,
                "matches": []
            }
        
        # Get match details and filter for ranked games
        ranked_matches = []
        for match_id in match_ids:
            try:
                match_data = self.get_match_details(match_id)
                info = match_data.get("info", {})
                game_mode = info.get("gameMode", "")
                game_queue_id = info.get("queueId", 0)
                
                # Filter for ranked games (queueId: 420 = Ranked Solo, 440 = Ranked Flex)
                if game_queue_id in [420, 440]:
                    ranked_matches.append({
                        "match_id": match_id,
                        "match_data": match_data
                    })
                    
                    # Stop if we have enough ranked matches
                    if len(ranked_matches) >= count:
                        break
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
            except ValueError as e:
                # Log error but continue with other matches
                print(f"Error fetching match {match_id}: {str(e)}")
                continue
        
        return {
            "game_name": game_name,
            "tag_line": tag_line,
            "puuid": puuid,
            "matches": ranked_matches
        }
    
    def get_player_matches(self, summoner_name, count=5):
        """
        Convenience method to get all match data for a player.
        
        Args:
            summoner_name (str): The summoner name
            count (int): Number of matches to retrieve (default: 5)
            
        Returns:
            dict: Dictionary containing player info and list of match details
                {
                    "summoner_name": str,
                    "puuid": str,
                    "matches": [
                        {
                            "match_id": str,
                            "match_data": dict
                        },
                        ...
                    ]
                }
            
        Raises:
            ValueError: If any error occurs during API calls
        """
        # Get PUUID
        puuid = self.get_puuid_by_name(summoner_name)
        
        # Get match IDs
        match_ids = self.get_match_ids_by_puuid(puuid, count)
        
        if not match_ids:
            return {
                "summoner_name": summoner_name,
                "puuid": puuid,
                "matches": []
            }
        
        # Get match details for each match
        matches = []
        for match_id in match_ids:
            try:
                match_data = self.get_match_details(match_id)
                matches.append({
                    "match_id": match_id,
                    "match_data": match_data
                })
                # Small delay to avoid rate limiting
                time.sleep(0.1)
            except ValueError as e:
                # Log error but continue with other matches
                print(f"Error fetching match {match_id}: {str(e)}")
                continue
        
        return {
            "summoner_name": summoner_name,
            "puuid": puuid,
            "matches": matches
        }
    
    def publish_match_event(
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
        enable_rabbitmq: bool = True,
    ) -> bool:
        """
        Publish a match ended event to RabbitMQ.
        
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
            enable_rabbitmq: Whether to enable RabbitMQ publishing
            
        Returns:
            True if published successfully, False otherwise
        """
        if not enable_rabbitmq:
            return False
        
        try:
            from publishers import MatchPublisher
            
            publisher = MatchPublisher()
            return publisher.publish_match_ended(
                match_id=match_id,
                puuid=puuid,
                summoner_name=summoner_name,
                game_duration=game_duration,
                win=win,
                champion=champion,
                kills=kills,
                deaths=deaths,
                assists=assists,
                kda=kda,
            )
        except Exception as e:
            print(f"Failed to publish match event: {e}")
            return False
    
    def get_and_publish_last_match(
        self,
        summoner_name: str,
        enable_rabbitmq: bool = True,
    ) -> Optional[dict]:
        """
        Get the last match for a player and publish it to RabbitMQ.
        
        Args:
            summoner_name: The summoner name
            enable_rabbitmq: Whether to enable RabbitMQ publishing
            
        Returns:
            Match data dictionary or None if failed
        """
        try:
            # Get PUUID
            puuid = self.get_puuid_by_name(summoner_name)
            
            # Get last match ID
            match_ids = self.get_match_ids_by_puuid(puuid, count=1)
            
            if not match_ids:
                print(f"No matches found for {summoner_name}")
                return None
            
            match_id = match_ids[0]
            match_data = self.get_match_details(match_id)
            info = match_data.get("info", {})
            
            # Find the player in the match
            participant = None
            for p in info.get("participants", []):
                if p.get("puuid") == puuid:
                    participant = p
                    break
            
            if not participant:
                print(f"Player {summoner_name} not found in match {match_id}")
                return None
            
            # Extract match data
            game_duration = info.get("gameDuration", 0)
            win = participant.get("win", False)
            champion_id = participant.get("championId", 0)
            kills = participant.get("kills", 0)
            deaths = participant.get("deaths", 0)
            assists = participant.get("assists", 0)
            
            # Calculate KDA
            kda = (kills + assists) / deaths if deaths > 0 else kills + assists
            
            # Get champion name from ID (simplified - you may need a champion mapping)
            champion = f"Champion_{champion_id}"
            
            # Publish to RabbitMQ
            if enable_rabbitmq:
                self.publish_match_event(
                    match_id=match_id,
                    puuid=puuid,
                    summoner_name=summoner_name,
                    game_duration=game_duration,
                    win=win,
                    champion=champion,
                    kills=kills,
                    deaths=deaths,
                    assists=assists,
                    kda=kda,
                )
            
            return {
                "match_id": match_id,
                "summoner_name": summoner_name,
                "puuid": puuid,
                "game_duration": game_duration,
                "win": win,
                "champion": champion,
                "kills": kills,
                "deaths": deaths,
                "assists": assists,
                "kda": kda,
            }
        except Exception as e:
            print(f"Error getting and publishing match: {e}")
            return None
