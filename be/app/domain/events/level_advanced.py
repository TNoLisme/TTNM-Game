from uuid import UUID

class LevelAdvanced:
    def __init__(self, session_id: UUID, new_level: int):
        self.session_id = session_id
        self.new_level = new_level