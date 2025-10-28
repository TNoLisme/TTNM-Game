from uuid import UUID
from typing import List, Dict, TYPE_CHECKING
from datetime import datetime
import enum

if TYPE_CHECKING:
    from app.domain.analytics.child_progress import ChildProgress
    from app.domain.games.question import Question

class SessionStateEnum(enum.Enum):
    playing = "playing"
    pause = "pause"
    end = "end"

class Session:
    def __init__(
        self,
        session_id: UUID,
        user_id: UUID,
        game_id: UUID,
        start_time: datetime,
        state: SessionStateEnum,
        score: int,
        emotion_errors: Dict[str, int],
        max_errors: int,
        level_threshold: int,
        ratio: List[float],
        time_limit: int,
        questions: List['Question']
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.game_id = game_id
        self.start_time = start_time
        self.end_time = None
        self.state = state
        self.score = score
        self.emotion_errors = emotion_errors
        self.max_errors = max_errors
        self.level_threshold = level_threshold
        self.ratio = ratio
        self.time_limit = time_limit
        self.questions = questions  # Danh sách 10 câu hỏi random từ đầu level

    def start_session(self, user_id: UUID, game_id: UUID) -> None:
        """Bắt đầu phiên chơi mới, random 10 câu hỏi."""
        from app.domain.games.question import Question  # Import runtime

        self.session_id = UUID("abc12345-e89b-12d3-a456-426614174000")
        self.user_id = user_id
        self.game_id = game_id
        self.start_time = datetime.now()
        self.state = SessionStateEnum.playing
        self.score = 0
        self.emotion_errors = {}
        self.ratio = []

        # Random 10 câu hỏi (placeholder)
        self.questions = [Question.get_random_contents(game_id, 1)[0] for _ in range(10)]

    def end_session(self) -> None:
        """Kết thúc phiên chơi, lưu ratio và review_emotions."""
        from app.domain.analytics.child_progress import ChildProgress  # Import runtime

        self.end_time = datetime.now()
        self.state = SessionStateEnum.end
        self.ratio = self.calculate_ratio(self.emotion_errors)

        child_progress: 'ChildProgress' = ChildProgress.load_progress(self.user_id, self.game_id)
        child_progress.update_emotion_distribution(self)

    def save_state(self, state: SessionStateEnum) -> None:
        """Lưu trạng thái phiên."""
        self.state = state

    def load_state(self, session_id: UUID) -> Dict:
        """Tải trạng thái phiên theo session_id."""
        return {"state": self.state.value, "score": self.score}

    def update_score(self, is_correct: bool) -> None:
        """Cập nhật điểm số dựa trên kết quả câu hỏi."""
        self.score += 10 if is_correct else 0

    def check_emotion_errors(self, errors: Dict[str, int], emotion: str) -> bool:
        """Kiểm tra lỗi cảm xúc, trả về true nếu cần ôn tập."""
        self.emotion_errors[emotion] = self.emotion_errors.get(emotion, 0) + 1
        return self.emotion_errors.get(emotion, 0) > self.max_errors

    def show_emotion_concept(self, emotion: str) -> None:
        """Hiển thị nội dung ôn tập cảm xúc."""
        # Placeholder: cần repository
        pass

    def calculate_ratio(self, errors: Dict[str, int]) -> List[float]:
        """Tính tỷ lệ xuất hiện cảm xúc."""
        total = sum(errors.values()) or 1
        return [errors.get(emotion, 0) / total for emotion in set(errors.keys())]

    def next_question_level(self) -> 'Question':
        """Lấy câu hỏi tiếp theo từ questions."""
        if not self.questions:
            raise ValueError("No questions available")
        return self.questions.pop(0)

    def advance_level(self, score: int) -> None:
        """Tăng level nếu điểm đạt level_threshold."""
        if score >= self.level_threshold:
            self.level += 1
            self.reset_emotion_errors({})

    def reset_emotion_errors(self, errors: Dict[str, int]) -> None:
        """Đặt lại emotion_errors khi lên level."""
        self.emotion_errors = errors
