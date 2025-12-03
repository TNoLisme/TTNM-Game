from uuid import UUID
from datetime import datetime
from app.domain.games.game import Game
from app.repository.games_repo import GamesRepository
from app.repository.game_contents_repo import GameContentsRepository
from app.mapper.games_mapper import GamesMapper
from app.domain.sessions.session import Session

class GameService():
    def __init__(self, db: Session):
        self.repo = GamesRepository(db)
        self.mapper = GamesMapper

    def get_by_id(self, game_id: str):
        game = self.repo.get_game_by_id(game_id)
        if not game:
            return None

        response = self.mapper.to_response(game)
        return response

    def update(self, game_id: str, data: dict) -> dict:
        game = self.repo.get_game_by_id(UUID(game_id))
        if game:
            game.name = data.get("name", game.name)
            game.level = data.get("level", game.level)
            self.repo.save(game)
            return {"status": "success", "message": f"Game {game.name} updated"}
        return {"status": "failed", "message": "Game not found"}

    
    def get_all_games(self) -> dict:
        games = self.repo.get_all()
        games_list = []

        for game in games:
            games_list.append({
                "game_id": str(game.game_id),
                "game_type": game.game_type,
                "name": game.name,
                "level": game.level,
                "difficulty_level": game.difficulty_level,
                "max_errors": game.max_errors,
                "level_threshold": game.level_threshold,
                "time_limit": game.time_limit
            })
        return games_list
