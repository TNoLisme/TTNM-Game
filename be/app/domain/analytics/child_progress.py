from uuid import UUID
from typing import List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.domain.sessions.session import Session
    from app.domain.sessions.emotion_concept import EmotionConcept

class ChildProgress:
    def __init__(
        self,
        progress_id: UUID,
        child_id: UUID,
        game_id: UUID,
        level: int,
        accuracy: float,
        avg_response_time: float,
        score: int,
        last_played: datetime,
        ratio: List[float],
        review_emotions: List[UUID]
    ):
        self.progress_id = progress_id
        self.child_id = child_id
        self.game_id = game_id
        self.level = level
        self.accuracy = accuracy
        self.avg_response_time = avg_response_time
        self.score = score
        self.last_played = last_played
        self.ratio = ratio
        self.review_emotions = review_emotions

    @classmethod
    def load_progress(cls, child_id: UUID, game_id: UUID) -> 'ChildProgress':
        """Tải tiến trình cho một trò chơi."""
        # Placeholder: cần repository
        return cls(
            UUID("jkl01234-e89b-12d3-a456-426614174000"),
            child_id,
            game_id,
            1,
            0.0,
            0.0,
            0,
            datetime.now(),
            [],
            []
        )

    def calculate_accuracy(self, sessions: List['Session']) -> float:
        """
        Tính tỷ lệ trả lời đúng (%) dựa trên danh sách các session.
        Accuracy = (Tổng số câu trả lời đúng) / (Tổng số câu trả lời) * 100
        """
        total_questions = 0
        total_correct = 0

        for session in sessions:
            questions = getattr(session, "session_questions", [])
            total_questions += len(questions)
            total_correct += sum(1 for q in questions if getattr(q, "is_correct", False))

        if total_questions == 0:
            print("Không có câu hỏi nào, accuracy = 0%")
            return 0.0

        accuracy = (total_correct / total_questions) * 100
        print(f"Tổng câu hỏi: {total_questions}, Đúng: {total_correct}, Accuracy mới: {accuracy:.2f}%")
        return accuracy


    def update_emotion_distribution(self) -> None:
        """Cập nhật phân bố cảm xúc."""
        print(" run vào  update_emotion_distribution")

    def generate_report(self, report_type: str) -> dict:
        """Tạo báo cáo tiến trình."""
        return {"type": report_type, "accuracy": self.accuracy}

    def check_level_advance(self, score: int, level_threshold: int) -> bool:
        """Kiểm tra xem có đủ điểm để lên level không."""
        return score >= level_threshold

    def get_review_emotions(self) -> List['EmotionConcept']:
        """Lấy danh sách EmotionConcept cần ôn tập."""
        from app.domain.sessions.emotion_concept import EmotionConcept  # import runtime
        return [EmotionConcept.load_concept_by_emotion_and_level(e, 1) for e in self.review_emotions]
