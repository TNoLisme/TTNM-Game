
from app.models.games.game_data_question import GameDataContents

class GameDataContentsMapper:
    @staticmethod
    def to_domain(model: GameDataContents) -> GameDataContents:
        if not model:
            return None
        return GameDataContents(
            data_id=model.data_id,
            question_id=model.question_id
        )

    @staticmethod
    def to_model(domain: GameDataContents) -> GameDataContents:
        if not domain:
            return None
        return GameDataContents(
            data_id=domain.data_id,
            question_id=domain.question_id
        )