from typing import List, Optional
from uuid import UUID
from game import Game
from models.sessions.session import Session
from models.sessions.game_data import GameData
from models.sessions.game_content import GameContent

class GameClick(Game):
    """
    GameClick kế thừa từ Game.
    Dùng cho trò chơi dạng chọn (click/multiple choice).
    """

    def __init__(
        self,
        data_of_game: Optional[GameData] = None,
        type_question: str = "sole_choice",
        answer_user: Optional[List[str]] = None,
        options: Optional[List[str]] = None,
        is_hard_level: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)
        self._data_of_game = data_of_game
        self._type_question = type_question
        self._answer_user = answer_user or []
        self._options = options or []
        self._is_hard_level = is_hard_level

    # ----- Override abstract methods từ Game -----

    def play(self, session: Session) -> None:
        """
        Hiển thị câu hỏi từ GameData và chờ người dùng chọn đáp án.
        Cập nhật session và score.
        """
        pass

    def continue_game(self, session: Session) -> None:
        """
        Tiếp tục game từ trạng thái session đã lưu.
        """
        pass

    def pause(self, session: Session) -> None:
        """
        Tạm dừng phiên chơi và lưu trạng thái vào session.
        """
        pass

    def end_game(self, session: Session) -> None:
        """
        Kết thúc phiên chơi và cập nhật session cuối.
        """
        pass

    def provide_hint(self, content: GameContent) -> None:
        """
        Hiển thị gợi ý từ GameContent nếu is_hint = True.
        """
        pass

    def check_emotion_errors(self, emotion_errors: dict, emotion: str) -> bool:
        """
        Kiểm tra số lỗi cảm xúc của người dùng.
        Nếu >= max_errors, trả về True để kích hoạt ôn tập.
        """
        pass

    def show_emotion_concept(self, emotion: str) -> None:
        """
        Hiển thị khái niệm cảm xúc liên quan.
        """
        pass

    def update_score(self, correct: bool) -> None:
        """
        Cập nhật điểm nếu người dùng trả lời đúng.
        """
        pass

    def calculate_ratio(self, emotion_errors: dict) -> List[float]:
        """
        Tính tỷ lệ xuất hiện từng cảm xúc trong level hiện tại.
        """
        pass

    def next_question_level(self, ratio: List[float], game_data: GameData) -> None:
        """
        Tải câu hỏi tiếp theo dựa trên tỷ lệ xuất hiện cảm xúc.
        """
        pass

    def advance_level(self, score: int) -> None:
        """
        Tăng level nếu điểm đạt ngưỡng level_threshold.
        """
        pass

    def reset_emotion_errors(self) -> None:
        """
        Đặt lại số lần sai cảm xúc khi lên level mới.
        """
        pass

    def get_info_game(self, session: Session) -> dict:
        """
        Trả về thông tin game cho thống kê từ session.
        """
        pass

    def get_question_data(self, game_id: UUID, level: int) -> GameData:
        """
        Lấy dữ liệu câu hỏi từ GameData theo game_id và level.
        """
        pass

    def get_data_by_level(self, level: int) -> GameData:
        """
        Lấy dữ liệu câu hỏi theo level hiện tại.
        """
        pass

    # ----- GameClick đặc thù -----

    def display_type_options(self, option_type: str, options: List[str]) -> None:
        """
        Hiển thị đáp án theo kiểu text, icon hoặc image.
        """
        pass

    def check_answer(self, user_answers: List[str], correct_answers: List[str]) -> List[bool]:
        """
        Kiểm tra từng đáp án người dùng chọn so với đáp án đúng.
        """
        pass
