from game_cv import GameCV
from models.sessions.session import Session

class GameExpressEmotion(GameCV):
    """
    Trò chơi yêu cầu trẻ thể hiện cảm xúc mục tiêu qua camera.
    Kế thừa từ GameCV.
    """

    def __init__(self, target_emotion: str, **kwargs):
        super().__init__(**kwargs)
        self._target_emotion = target_emotion

    def play(self, session: Session) -> None:
        """
        Hiển thị cảm xúc mục tiêu.
        Ghi hình người chơi và xác thực cảm xúc.
        """
        pass
