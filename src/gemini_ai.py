"""
Gemini AI Integration Module
Handles all communications with Google Gemini API for AI analysis using direct HTTP requests.
"""

import requests
import json


class GeminiAI:
    """Class to interact with Google Gemini API for AI analysis using direct API calls."""
    
    def __init__(self, api_key):
        """
        Initialize Gemini AI client.
        
        Args:
            api_key (str): Google Gemini API key
        """
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent"
    
    def initialize(self):
        """
        Initialize Gemini client (placeholder for API calls).
        With direct API calls, initialization is done at request time.
        """
        pass
    
    def analyze_lol_matches(self, match_data, player_name):
        """
        Send match data to Gemini and get AI analysis.
        
        Args:
            match_data (dict): Match data from Riot API
            player_name (str): The player's summoner name
            
        Returns:
            str: AI-generated analysis in Vietnamese
            
        Raises:
            ValueError: If API error occurs
        """
        # Prepare match data summary for the prompt
        matches_summary = self._prepare_match_summary(match_data)
        
        # Create the prompt
        prompt = self._create_prompt(player_name, matches_summary)
        
        try:
            # Prepare the request payload
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 8192
                }
            }
            
            # Make the API request
            url = f"{self.base_url}?key={self.api_key}"
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 401:
                raise ValueError("API key không hợp lệ hoặc đã hết hạn")
            elif response.status_code == 429:
                raise ValueError("Đã vượt quá giới hạn API. Vui lòng thử lại sau")
            elif response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', response.text)
                raise ValueError(f"Lỗi API: {response.status_code} - {error_msg}")
            
            # Parse the response
            result = response.json()
            
            # Extract the generated text
            candidates = result.get('candidates', [])
            if not candidates:
                raise ValueError("Không nhận được phản hồi từ AI")
            
            content = candidates[0].get('content', {})
            parts = content.get('parts', [])
            if not parts:
                raise ValueError("Không nhận được nội dung phản hồi từ AI")
            
            generated_text = parts[0].get('text', '')
            if not generated_text:
                raise ValueError("Nội dung phản hồi trống")
            
            return generated_text.strip()
            
        except requests.exceptions.Timeout:
            raise ValueError("Yêu cầu hết thời gian chờ. Vui lòng thử lại")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Lỗi kết nối: {str(e)}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Lỗi phân tích phản hồi: {str(e)}")
    
    def analyze_lol_rank(self, rank_data):
        """
        Send rank data to Gemini and get AI analysis.
        
        Args:
            rank_data (dict): Rank data from Riot API
                {
                    "game_name": str,
                    "tag_line": str,
                    "puuid": str,
                    "league_entries": list
                }
            
        Returns:
            str: AI-generated analysis in Vietnamese
            
        Raises:
            ValueError: If API error occurs
        """
        # Prepare rank data summary for the prompt
        rank_summary = self._prepare_rank_summary(rank_data)
        
        # Create the prompt
        prompt = self._create_rank_prompt(rank_data["game_name"], rank_data["tag_line"], rank_summary)
        
        try:
            # Prepare the request payload
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 4096
                }
            }
            
            # Make the API request
            url = f"{self.base_url}?key={self.api_key}"
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 401:
                raise ValueError("API key không hợp lệ hoặc đã hết hạn")
            elif response.status_code == 429:
                raise ValueError("Đã vượt quá giới hạn API. Vui lòng thử lại sau")
            elif response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', response.text)
                raise ValueError(f"Lỗi API: {response.status_code} - {error_msg}")
            
            # Parse the response
            result = response.json()
            
            # Extract the generated text
            candidates = result.get('candidates', [])
            if not candidates:
                raise ValueError("Không nhận được phản hồi từ AI")
            
            content = candidates[0].get('content', {})
            parts = content.get('parts', [])
            if not parts:
                raise ValueError("Không nhận được nội dung phản hồi từ AI")
            
            generated_text = parts[0].get('text', '')
            if not generated_text:
                raise ValueError("Nội dung phản hồi trống")
            
            return generated_text.strip()
            
        except requests.exceptions.Timeout:
            raise ValueError("Yêu cầu hết thời gian chờ. Vui lòng thử lại")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Lỗi kết nối: {str(e)}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Lỗi phân tích phản hồi: {str(e)}")
    
    def _prepare_rank_summary(self, rank_data):
        """
        Prepare a readable summary of rank data for the AI prompt.
        
        Args:
            rank_data (dict): Rank data from Riot API
            
        Returns:
            str: Formatted rank summary
        """
        league_entries = rank_data.get("league_entries", [])
        
        if not league_entries:
            return "Người chơi này chưa có xếp hạng (Unranked)."
        
        summary_parts = []
        
        for entry in league_entries:
            queue_type = entry.get("queueType", "Unknown")
            tier = entry.get("tier", "Unranked")
            rank = entry.get("rank", "")
            league_points = entry.get("leaguePoints", 0)
            wins = entry.get("wins", 0)
            losses = entry.get("losses", 0)
            veteran = entry.get("veteran", False)
            inactive = entry.get("inactive", False)
            fresh_blood = entry.get("freshBlood", False)
            hot_streak = entry.get("hotStreak", False)
            
            # Calculate win rate
            total_games = wins + losses
            win_rate = (wins / total_games * 100) if total_games > 0 else 0
            
            # Queue type description
            queue_names = {
                "RANKED_SOLO_5x5": "Đơn/Đôi (Solo/Duo)",
                "RANKED_FLEX_SR": "Linh hoạt (Flex)",
                "RANKED_TFT": "Teamfight Tactics",
                "RANKED_FLEX_TT": "Linh hoạt 3v3"
            }
            queue_name = queue_names.get(queue_type, queue_type)
            
            entry_summary = f"""
Queue: {queue_name}
- Xếp hạng: {tier} {rank}
- Điểm LP: {league_points}
- Số trận: {wins} thắng / {losses} thua (Tổng: {total_games})
- Tỷ lệ thắng: {win_rate:.1f}%
- Cờ: {', '.join([x for x in ['Veteran', 'Inactive', 'Fresh Blood', 'Hot Streak'] if [veteran, inactive, fresh_blood, hot_streak][['Veteran', 'Inactive', 'Fresh Blood', 'Hot Streak'].index(x)]])}
"""
            summary_parts.append(entry_summary)
        
        return "\n".join(summary_parts)
    
    def _create_rank_prompt(self, game_name, tag_line, rank_summary):
        """
        Create the prompt for Gemini AI for rank analysis.
        
        Args:
            game_name (str): The player's game name
            tag_line (str): The player's tag line
            rank_summary (str): Formatted rank summary
            
        Returns:
            str: The complete prompt
        """
        prompt = f"""Mày là một thằng toxic chuyên phân tích game League of Legends. Mày hay chửi bậy, mắng người ta ngu, troll không thương tiếc nhưng vẫn đưa ra phân tích đúng.

Giọng điệu của mày: cực kỳ toxic, hay chửi thề, mắng người ta đồ noob, đồ gà, đồ ngu, troll hết cỡ. Dùng các từ như "đ*t mẹ", "ngu vl", "gà vãi", "trash", "noob", "ăn hành", "feed như chó", "đội lỗ ăn mắm", v.v.

Bây giờ hãy phân tích xếp hạng hiện tại của thằng "{game_name}#{tag_line}".

Dưới đây là dữ liệu chi tiết về xếp hạng:

{rank_summary}

Dựa trên dữ liệu trên, hãy cung cấp phân tích bằng tiếng Việt với các phần sau (nhớ toxic và troll hết cỡ):

1. **🤡 TỔNG QUAN XẾP HẠNG**
   - Xếp hạng hiện tại ở các chế độ (chê bai hết mức có thể)
   - Đánh giá chung về trình độ (mắng nó ngu nếu rank thấp)

2. **💩 ĐÁNH GIÁ HIỆU SUẤT**
   - Phân tích tỷ lệ thắng (nếu thấp thì chửi cho mạnh vào)
   - Đánh giá số trận đã chơi (chơi nhiều mà vẫn gà thì càng phải chửi)

3. **🔥 GỢI Ý CẢI THIỆN (NẾU CÒN CỨU ĐƯỢC)**
   - Lời khuyên để leo rank (có thể khuyên nên bỏ game nếu quá gà)
   - Gợi ý về cách chơi để tăng điểm

4. **🎯 MỤC TIÊU VÀ ĐỊNH HƯỚNG**
   - Đề xuất mục tiêu xếp hạng phù hợp (đừng quá ảo tưởng)
   - Lời khuyên để duy trì phong độ (hoặc khuyên bỏ game)

Hãy viết phân tích toxic hết cỡ, chửi bậy thoải mái, mắng mỏ đồ ngu nhưng vẫn đưa ra phân tích chính xác. Sử dụng emoji để làm nổi bật sự toxic 🔥💀🤡💩."""
        
        return prompt
    
    def _prepare_match_summary(self, match_data):
        """
        Prepare a readable summary of match data for the AI prompt.
        
        Args:
            match_data (dict): Match data from Riot API
            
        Returns:
            str: Formatted match summary
        """
        if not match_data.get("matches"):
            return "Người chơi này chưa có trận đấu nào gần đây."
        
        summary_parts = []
        
        for idx, match_info in enumerate(match_data["matches"], 1):
            match = match_info["match_data"]
            info = match.get("info", {})
            
            # Get game duration in minutes
            duration = info.get("gameDuration", 0) / 60
            
            # Get game mode
            game_mode = info.get("gameMode", "Unknown")
            game_type = info.get("gameType", "Unknown")
            
            # Find the player in participants
            player_puuid = match_data.get("puuid", "")
            player_data = None
            
            for participant in info.get("participants", []):
                if participant.get("puuid") == player_puuid:
                    player_data = participant
                    break
            
            if player_data:
                # Player stats
                champion_name = player_data.get("championName", "Unknown")
                kills = player_data.get("kills", 0)
                deaths = player_data.get("deaths", 0)
                assists = player_data.get("assists", 0)
                win = player_data.get("win", False)
                
                # Gold and damage
                gold_earned = player_data.get("goldEarned", 0)
                total_damage = player_data.get("totalDamageDealtToChampions", 0)
                
                # Items
                items = []
                for i in range(6):
                    item = player_data.get(f"item{i}", 0)
                    if item:
                        items.append(str(item))
                
                # Position
                position = player_data.get("individualPosition", "Unknown")
                
                # Team info
                team_id = player_data.get("teamId", 0)
                team = None
                for t in info.get("teams", []):
                    if t.get("teamId") == team_id:
                        team = t
                        break
                
                # Team objectives
                baron_kills = team.get("baronKills", 0) if team else 0
                dragon_kills = team.get("dragonKills", 0) if team else 0
                tower_kills = team.get("towerKills", 0) if team else 0
                
                match_summary = f"""
Trận đấu {idx}:
- Kết quả: {'Thắng' if win else 'Thua'}
- Thời gian: {duration:.1f} phút
- Chế độ chơi: {game_mode}
- Vị trí: {position}
- Tướng: {champion_name}
- KDA: {kills}/{deaths}/{assists}
- Vàng kiếm được: {gold_earned}
- Sát thương gây ra cho tướng: {total_damage}
- Trang bị: {', '.join(items) if items else 'Không có'}
- Team: Baron {baron_kills}, Rồng {dragon_kills}, Tháp {tower_kills}
"""
            else:
                match_summary = f"""
Trận đấu {idx}:
- Không tìm thấy dữ liệu người chơi trong trận này
"""
            
            summary_parts.append(match_summary)
        
        return "\n".join(summary_parts)
    
    def _create_prompt(self, player_name, matches_summary):
        """
        Create the prompt for Gemini AI.
        
        Args:
            player_name (str): The player's summoner name
            matches_summary (str): Formatted match summary
            
        Returns:
            str: The complete prompt
        """
        prompt = f"""Mày là một thằng toxic chuyên phân tích game League of Legends. Mày hay chửi bậy, mắng người ta ngu, troll không thương tiếc nhưng vẫn đưa ra phân tích đúng.

Giọng điệu của mày: cực kỳ toxic, hay chửi thề, mắng người ta đồ noob, đồ gà, đồ ngu, troll hết cỡ. Dùng các từ như "đ*t mẹ", "ngu vl", "gà vãi", "trash", "noob", "ăn hành", "feed như chó", "đội lỗ ăn mắm", "cân não đéo có não", v.v.

Bây giờ hãy phân tích các trận đấu gần nhất của thằng "{player_name}".

Dưới đây là dữ liệu chi tiết của các trận đấu:

{matches_summary}

Dựa trên dữ liệu trên, hãy cung cấp phân tích bằng tiếng Việt với các phần sau (nhớ toxic và troll hết cỡ):

1. **🤡 TỔNG QUAN HIỆU SUẤT**
   - Tỷ lệ thắng/thua (mắng cho mạnh nếu thua nhiều)
   - Đánh giá chung về phong độ (chửi nếu chơi như sh*t)

2. **💪 ĐIỂM MẠNH (NẾU CÓ)**
   - Những điểm nổi bật trong lối chơi (khó tìm lắm với mấy thằng gà)
   - Những tướng chơi tốt (nếu có thì khen nửa miệng)

3. **💩 ĐIỂM YẾU (CHẮC CHẮN CÓ NHIỀU)**
   - Những vấn đề cần khắc phục (chửi cho mạnh vào)
   - Những tình huống thường xuyên mắc lỗi (feed, int, throw game)

4. **🔥 GỢI Ý CẢI THIỆN (NẾU CÒN CỨU ĐƯỢC)**
   - Đề xuất về việc chọn tướng (đừng pick mấy con mày đéo biết chơi)
   - Gợi ý về cách build trang bị (build như cc thế ai chịu được)
   - Lời khuyên về chiến thuật và vị trí (hay nghĩ mình carry được à?)

5. **🎭 MẪU HÀNH VI**
   - Những điểm chung qua các trận đấu (toàn thói xấu)
   - Thói quen chơi game (tốt thì ít, xấu thì nhiều vl)

Hãy viết phân tích toxic hết cỡ, chửi bậy thoải mái, mắng mỏ đồ ngu nhưng vẫn đưa ra phân tích chính xác. Sử dụng emoji để làm nổi bật sự toxic 🔥💀🤡💩🗑️."""
        
        return prompt
    
    def ask_lol_question(self, rank_data, match_data, player_display, question):
        """
        Send rank and match data with a custom question to Gemini and get AI answer.
        
        Args:
            rank_data (dict): Rank data from Riot API
            match_data (dict): Match data from Riot API
            player_display (str): The player's display name (gameName#tagLine)
            question (str): The custom question to ask AI
            
        Returns:
            str: AI-generated answer in Vietnamese
            
        Raises:
            ValueError: If API error occurs
        """
        # Prepare data summaries for the prompt
        rank_summary = self._prepare_rank_summary(rank_data)
        matches_summary = self._prepare_match_summary(match_data)
        
        # Create the prompt with custom question
        prompt = self._create_ask_prompt(player_display, rank_summary, matches_summary, question)
        
        try:
            # Prepare the request payload
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 8192
                }
            }
            
            # Make the API request
            url = f"{self.base_url}?key={self.api_key}"
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 401:
                raise ValueError("API key không hợp lệ hoặc đã hết hạn")
            elif response.status_code == 429:
                raise ValueError("Đã vượt quá giới hạn API. Vui lòng thử lại sau")
            elif response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', response.text)
                raise ValueError(f"Lỗi API: {response.status_code} - {error_msg}")
            
            # Parse the response
            result = response.json()
            
            # Extract the generated text
            candidates = result.get('candidates', [])
            if not candidates:
                raise ValueError("Không nhận được phản hồi từ AI")
            
            content = candidates[0].get('content', {})
            parts = content.get('parts', [])
            if not parts:
                raise ValueError("Không nhận được nội dung phản hồi từ AI")
            
            generated_text = parts[0].get('text', '')
            if not generated_text:
                raise ValueError("Nội dung phản hồi trống")
            
            return generated_text.strip()
            
        except requests.exceptions.Timeout:
            raise ValueError("Yêu cầu hết thời gian chờ. Vui lòng thử lại")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Lỗi kết nối: {str(e)}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Lỗi phân tích phản hồi: {str(e)}")
    
    def _create_ask_prompt(self, player_display, rank_summary, matches_summary, question):
        """
        Create the prompt for Gemini AI with a custom question.
        
        Args:
            player_display (str): The player's display name
            rank_summary (str): Formatted rank summary
            matches_summary (str): Formatted match summary
            question (str): The custom question to ask
            
        Returns:
            str: The complete prompt
        """
        prompt = f"""Mày là một thằng toxic chuyên phân tích game League of Legends. Mày hay chửi bậy, mắng người ta ngu, troll không thương tiếc nhưng vẫn đưa ra phân tích đúng.

Giọng điệu của mày: cực kỳ toxic, hay chửi thề, mắng người ta đồ noob, đồ gà, đồ ngu, troll hết cỡ. Dùng các từ như "đ*t mẹ", "ngu vl", "gà vãi", "trash", "noob", "ăn hành", "feed như chó", "đội lỗ ăn mắm", "cân não đéo có não", v.v.

Bây giờ hãy trả lời câu hỏi về thằng "{player_display}".

Dưới đây là dữ liệu chi tiết về thằng gà này:

**🤡 THÔNG TIN XẾP HẠNG:**
{rank_summary}

**💩 5 TRẬN ĐẤU GẦN NHẤT:**
{matches_summary}

**❓ CÂU HỎI CỦA NGƯỜI DÙNG:**
{question}

Dựa trên dữ liệu trên, hãy trả lời câu hỏi bằng tiếng Việt theo phong cách toxic, chửi bậy thoải mái, mắng mỏ đồ ngu nhưng vẫn đưa ra câu trả lời chính xác. Sử dụng emoji để làm nổi bật sự toxic 🔥💀🤡💩🗑️. Nếu câu hỏi liên quan đến việc chơi dở thì chửi cho mạnh vào!"""
        
        return prompt
