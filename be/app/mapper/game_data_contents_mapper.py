# mapper/games/game_data_contents_mapper.py
from app.models.games.game_data_contents import GameDataContents
from app.domain.games.game_data_contents import GameDataContents as GameDataContentsDomain

class GameDataContentsMapper:
    @staticmethod
    def to_domain(model: GameDataContents) -> GameDataContentsDomain:
        if not model:
            return None
        return GameDataContentsDomain(
            data_id=model.data_id,
            content_id=model.content_id
        )

    @staticmethod
    def to_model(domain: GameDataContentsDomain) -> GameDataContents:
        if not domain:
            return None
        return GameDataContents(
            data_id=domain.data_id,
            content_id=domain.content_id
        )