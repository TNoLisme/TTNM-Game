# domain/games/game_data_contents.py
class GameDataContents:
    def __init__(self, data_id: str, content_id: str):
        self.data_id = data_id
        self.content_id = content_id

    def __repr__(self):
        return f"GameDataContents(data_id={self.data_id}, content_id={self.content_id})"