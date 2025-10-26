from uuid import UUID
from typing import List
from app.domain.games.question import Question

class SessionStarted:
    def __init__(self, session_id: UUID, questions: List[Question]):
        self.session_id = session_id
        self.questions = questions