from uuid import UUID
from typing import Dict
from typing import List
from datetime import datetime
from ..games.question import Question

class SessionQuestions:
    def __init__(self, id: UUID, session_id: UUID, question_id: UUID, user_answer: Dict,
                 correct_answer: Dict, is_correct: bool, response_time_ms: int, check_hint: bool,
                 cv_confidence: float, timestamp: datetime):
        self.id = id
        self.session_id = session_id
        self.question_id = question_id
        self.user_answer = user_answer
        self.correct_answer = correct_answer
        self.is_correct = is_correct
        self.response_time_ms = response_time_ms
        self.check_hint = check_hint
        self.cv_confidence = cv_confidence
        self.timestamp = timestamp
