from typing import Dict
from game_click import GameClick
from models.sessions.session import Session

class GameWhoIsWho(GameClick):
    """
    Trò chơi nhiều khuôn mặt, trẻ phải khớp tên với cảm xúc.
    Kế thừa từ GameClick.
    """

    def play(self, session: Session) -> None:
        """
        Hiển thị nhiều khuôn mặt từ GameData.
        Yêu cầu trẻ khớp tên - cảm xúc.
        """
        pass

    def validate_matches(self, matches: Dict[str, str]) -> bool:
        """
        Kiểm tra các cặp tên - cảm xúc có đúng không.
        """
        pass
