from uuid import UUID

class GameCompleted:
    def __init__(self, session_id: UUID, score: int, level: int):
        self.session_id = session_id
        self.score = score
        self.level = level