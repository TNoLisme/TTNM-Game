from typing import Optional
from game_click import GameClick
from models.sessions.session import Session

class GameRecognizeEmotion(GameClick):
    """
    Trò chơi yêu cầu trẻ nhận diện cảm xúc và chọn đáp án đúng.
    Kế thừa từ GameClick.
    """

    def play(self, session: Session) -> None:
        """
        Hiển thị nội dung từ GameData.
        Yêu cầu trẻ chọn cảm xúc đúng.
        Cập nhật session và score.
        """
        pass
