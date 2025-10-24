from game import Game
from models.sessions.session import Session
from models.sessions.game_content import GameContent
from models.sessions.game_data import GameData
from typing import Optional
from uuid import UUID

class GameCV(Game):
    """
    GameCV kế thừa từ Game.
    Dùng cho trò chơi nhận diện cảm xúc qua camera (Computer Vision).
    """

    def __init__(self, cv_model: Optional[object] = None, camera_stream: Optional[object] = None, **kwargs):
        super().__init__(**kwargs)
        self._cv_model = cv_model
        self._camera_stream = camera_stream

    # ----- Override abstract methods từ Game -----

    def play(self, session: Session) -> None:
        """
        Hiển thị câu hỏi từ GameData, ghi hình người chơi,
        phân tích cảm xúc bằng cv_model, cập nhật session và score.
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
        """
        pass

    def show_emotion_concept(self, emotion: str) -> None:
        """
        Hiển thị khái niệm cảm xúc liên quan.
        """
        pass

    def update_score(self, correct: bool) -> None:
        """
        Cập nhật điểm nếu người dùng trả lời đúng hoặc thể hiện đúng cảm xúc.
        """
        pass

    def calculate_ratio(self, emotion_errors: dict) -> list[float]:
        """
        Tính tỷ lệ xuất hiện từng cảm xúc trong level hiện tại.
        """
        pass

    def next_question_level(self, ratio: list[float], game_data: GameData) -> None:
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

    # ----- GameCV đặc thù -----

    def process_cv_input(self, frame: object) -> str:
        """
        Phân tích khung hình, trả về cảm xúc người chơi.
        """
        pass

    def start_camera(self) -> None:
        """
        Khởi động luồng camera.
        """
        pass

    def stop_camera(self) -> None:
        """
        Dừng luồng camera.
        """
        pass

    def check_answer(self, predicted: str, correct: str) -> bool:
        """
        Kiểm tra cảm xúc dự đoán so với cảm xúc đúng.
        """
        pass
