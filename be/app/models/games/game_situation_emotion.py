from game_click import GameClick
from models.sessions.session import Session

class GameSituationEmotion(GameClick):
    """
    Trò chơi dựa trên tình huống, trẻ chọn cảm xúc phù hợp.
    Kế thừa từ GameClick.
    """

    def play(self, session: Session) -> None:
        """
        Hiển thị tình huống từ GameData.
        Trẻ chọn cảm xúc đúng.
        Cập nhật session và score.
        """
        pass
