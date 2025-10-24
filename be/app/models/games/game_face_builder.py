from typing import Dict
from game_click import GameClick
from models.sessions.session import Session

class GameFaceBuilder(GameClick):
    """
    Trò chơi ghép khuôn mặt theo cảm xúc.
    Kế thừa từ GameClick.
    """

    def play(self, session: Session) -> None:
        """
        Hiển thị tình huống từ GameData.
        Yêu cầu ghép các bộ phận khuôn mặt đúng.
        """
        pass

    def validate_face(self, selected_parts: Dict[str, str]) -> bool:
        """
        Kiểm tra các bộ phận được chọn có đúng với cảm xúc yêu cầu.
        """
        pass
