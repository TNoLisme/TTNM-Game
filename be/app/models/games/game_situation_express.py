from game_cv import GameCV
from models.sessions.session import Session

class GameSituationExpress(GameCV):
    """
    Trò chơi yêu cầu trẻ thể hiện cảm xúc theo tình huống.
    Kế thừa từ GameCV.
    """

    def play(self, session: Session) -> None:
        """
        Hiển thị tình huống từ GameData.
        Ghi hình và xác thực cảm xúc.
        """
        pass
