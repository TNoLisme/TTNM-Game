from uuid import UUID
from typing import List

class SessionEnded:
    def __init__(self, session_id: UUID, ratio: List[float], review_emotions: List[UUID]):
        self.session_id = session_id
        self.ratio = ratio
        self.review_emotions = review_emotions