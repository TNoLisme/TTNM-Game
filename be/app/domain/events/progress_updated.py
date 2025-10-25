from uuid import UUID
from typing import List

class ProgressUpdated:
    def __init__(self, child_id: UUID, game_id: UUID, ratio: List[float], review_emotions: List[UUID]):
        self.child_id = child_id
        self.game_id = game_id
        self.ratio = ratio
        self.review_emotions = review_emotions