from uuid import UUID
from typing import List
from datetime import datetime
import enum
from domain.sessions.session import Session
from domain.sessions.emotion_concept import EmotionConcept
class ChildProgress:
    def __init__(self, progress_id: UUID, child_id: UUID, game_id: UUID, level: int, accuracy: float,
                 avg_response_time: float, score: int, last_played: datetime, ratio: List[float],
                 review_emotions: List[UUID]):
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
        return cls(UUID("jkl01234-e89b-12d3-a456-426614174000"), child_id, game_id, 1, 0.0, 0.0, 0, datetime.now(), [], [])

    def calculate_accuracy(self, sessions: List[Session]) -> float:
        """Tính tỷ lệ trả lời đúng."""
        if not sessions:
            return 0.0
        correct = sum(1 for s in sessions for q in s.session_questions if q.is_correct)
        total = sum(len(s.session_questions) for s in sessions)
        return (correct / total) * 100 if total else 0.0

    def update_emotion_distribution(self, session: Session) -> None:
        """Cập nhật phân bố cảm xúc."""
        self.ratio = session.ratio
        self.review_emotions = [c.concept_id for c in self.get_review_emotions() if session.check_emotion_errors(session.emotion_errors, c.emotion)]

    def generate_report(self, report_type: str) -> dict:
        """Tạo báo cáo tiến trình."""
        # Placeholder
        return {"type": report_type, "accuracy": self.accuracy}

    def check_level_advance(self, score: int, level_threshold: int) -> bool:
        """Kiểm tra xem có đủ điểm để lên level không."""
        return score >= level_threshold

    def get_review_emotions(self) -> List['EmotionConcept']:
        """Lấy danh sách EmotionConcept cần ôn tập."""
        # Placeholder: cần repository
        from domain.sessions.emotion_concept import EmotionConcept
        return [EmotionConcept.load_concept_by_emotion_and_level(e, 1) for e in self.review_emotions]