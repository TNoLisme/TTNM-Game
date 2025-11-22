# domain/games/game_data_contents.py
class GameDataContents:
    def __init__(self, data_id: str, question_id: str):
        self.data_id = data_id
        self.question_id = question_id

    def __repr__(self):
        return f"GameDataContents(data_id={self.data_id}, question_id={self.question_id})"