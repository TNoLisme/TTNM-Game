from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from datetime import datetime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.domain.sessions.session import Session

class Game(ABC):
    def __init__(self, game_id: UUID, game_type: str, name: str, level: int, difficulty_level: int,
                 max_errors: int, level_threshold: int, time_limit: int):
        self.game_id = game_id
        self.game_type = game_type
        self.name = name
        self.level = level
        self.difficulty_level = difficulty_level
        self.max_errors = max_errors
        self.level_threshold = level_threshold
        self.time_limit = time_limit

    def play(self, session: 'Session') -> None:
        """Bắt đầu hoặc tiếp tục phiên chơi, sử dụng trạng thái từ Session."""
        if not session:
            raise ValueError("Session is required")
        self._validate_session(session)
        session.update_score(self._check_answer(session))

    def initialize_session(self, session: 'Session') -> None:
        """Sao chép cấu hình vào Session khi bắt đầu."""
        session.max_errors = self.max_errors
        session.level_threshold = self.level_threshold
        session.time_limit = self.time_limit

    @abstractmethod
    def _check_answer(self, session: 'Session') -> bool:
        """Kiểm tra đáp án, triển khai cụ thể bởi class con."""
        pass

    def _validate_session(self, session: 'Session') -> None:
        """Kiểm tra tính hợp lệ của session."""
        if session.game_id != self.game_id:
            raise ValueError("Session game_id does not match")

class GameClick(Game):
    def __init__(self, game_id: UUID, game_type: str, name: str, level: int, difficulty_level: int,
                 max_errors: int, level_threshold: int, time_limit: int, type_question: str, options: list):
        super().__init__(game_id, game_type, name, level, difficulty_level, max_errors, level_threshold, time_limit)
        self.type_question = type_question
        self.options = options
        self.is_hard_level = difficulty_level > 5

    def _check_answer(self, session: 'Session') -> bool:
        """Kiểm tra đáp án cho GameClick."""
        current_question = session.next_question_level()
        user_answer = session.session_questions[-1].user_answer.get("emotion") if session.session_questions else None
        correct_answer = current_question.correct_answer
        return user_answer == correct_answer

    def display_type_options(self, type: str, options: list) -> None:
        """Hiển thị các lựa chọn dạng text, icon hoặc image."""
        if type not in ["multiple_choice", "sole_choice"]:
            raise ValueError("Invalid type")
        self.options = options

    def check_answer(self, user_answers: list, correct_answers: list) -> list:
        """Kiểm tra đáp án người dùng, trả về mảng kết quả đúng/sai."""
        return [ua == ca for ua, ca in zip(user_answers, correct_answers)]

class GameCV(Game):
    def __init__(self, game_id: UUID, game_type: str, name: str, level: int, difficulty_level: int,
                 max_errors: int, level_threshold: int, time_limit: int, cv_model: dict, camera_stream: dict):
        super().__init__(game_id, game_type, name, level, difficulty_level, max_errors, level_threshold, time_limit)
        self.cv_model = cv_model
        self.camera_stream = camera_stream

    def _check_answer(self, session: 'Session') -> bool:
        """Kiểm tra đáp án cho GameCV."""
        current_question = session.next_question_level()
        user_answer = self.process_cv_input(session)
        return user_answer == current_question.correct_answer

    def process_cv_input(self, session: 'Session') -> str:
        """Phân tích khung hình từ camera, trả về cảm xúc."""
        if not self.camera_stream:
            raise ValueError("Camera stream is not initialized")
        return "vui"  # Placeholder, cần tích hợp mô hình AI thực tế

    def start_camera(self) -> None:
        """Khởi động luồng camera."""
        self.camera_stream = {"status": "active"}

    def stop_camera(self) -> None:
        """Dừng luồng camera."""
        self.camera_stream = None

# Các class con cụ thể của GameClick và GameCV
class GameRecognizeEmotion(GameClick):
    def _check_answer(self, session: 'Session') -> bool:
        return super()._check_answer(session)

class GameSituationEmotion(GameClick):
    def _check_answer(self, session: 'Session') -> bool:
        return super()._check_answer(session)

class GameFaceBuilder(GameClick):
    def _check_answer(self, session: 'Session') -> bool:
        return super()._check_answer(session)

    def validate_face(self, face_parts: dict) -> bool:
        """Kiểm tra các bộ phận khuôn mặt."""
        return bool(face_parts)

class GameWhoIsWho(GameClick):
    def _check_answer(self, session: 'Session') -> bool:
        return super()._check_answer(session)

    def validate_matches(self, matches: dict) -> bool:
        """Kiểm tra các cặp tên-cảm xúc."""
        return bool(matches)

class GameExpressEmotion(GameCV):
    def __init__(self, game_id: UUID, game_type: str, name: str, level: int, difficulty_level: int,
                 max_errors: int, level_threshold: int, time_limit: int, cv_model: dict, camera_stream: dict,
                 target_emotion: str):
        super().__init__(game_id, game_type, name, level, difficulty_level, max_errors, level_threshold, time_limit, cv_model, camera_stream)
        self.target_emotion = target_emotion

    def _check_answer(self, session: 'Session') -> bool:
        return super()._check_answer(session)

class GameSituationExpress(GameCV):
    def _check_answer(self, session: 'Session') -> bool:
        return super()._check_answer(session)