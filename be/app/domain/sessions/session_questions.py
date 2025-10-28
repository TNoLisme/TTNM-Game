from uuid import UUID
from typing import Dict
from typing import List
from datetime import datetime
from app.domain.games.question import Question

class SessionQuestions:
    def __init__(self, id: UUID, session_id: UUID, question: Question, user_answer: Dict,
                 correct_answer: Dict, is_correct: bool, response_time_ms: int, check_hint: bool,
                 cv_confidence: float, timestamp: datetime):
        self.id = id
        self.session_id = session_id
        self.question = question
        self.user_answer = user_answer
        self.correct_answer = correct_answer
        self.is_correct = is_correct
        self.response_time_ms = response_time_ms
        self.check_hint = check_hint
        self.cv_confidence = cv_confidence
        self.timestamp = timestamp

    @classmethod
    def save_question(cls, session_id: UUID, question: Question, user_answer: Dict, correct_answer: Dict,
                     is_correct: bool, response_time_ms: int, check_hint: bool, cv_confidence: float) -> 'SessionQuestions':
        """Lưu thông tin câu hỏi và đáp án vào phiên."""
        return cls(UUID("def45678-e89b-12d3-a456-426614174000"), session_id, question, user_answer,
                   correct_answer, is_correct, response_time_ms, check_hint, cv_confidence, datetime.now())

    @classmethod
    def get_questions_by_session(cls, session_id: UUID) -> List['SessionQuestions']:
        """Lấy danh sách câu hỏi trong phiên."""
        # Placeholder: cần repository
        return []