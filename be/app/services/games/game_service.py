from uuid import UUID
from datetime import datetime
from .base_game_service import BaseGameService
from domain.games.game import Game
from repository.games_repo import GameRepository

class GameService(BaseGameService):
    def __init__(self, game_repo: GameRepository):
        super().__init__(game_repo)

    def create(self, data: dict) -> dict:
        game = Game(
            game_id=UUID(data.get("game_id")),
            game_type=data.get("game_type"),
            name=data.get("name"),
            level=data.get("level"),
            difficulty_level=data.get("difficulty_level"),
            max_errors=data.get("max_errors"),
            level_threshold=data.get("level_threshold"),
            time_limit=data.get("time_limit")
        )
        self.repo.save_game(game)
        return {"status": "success", "message": f"Game {game.name} created", "game_id": str(game.game_id)}

    def get_by_id(self, game_id: str) -> dict:
        game = self.repo.get_game_by_id(UUID(game_id))
        if game:
            return {"status": "success", "data": {
                "game_id": str(game.game_id),
                "game_type": game.game_type,
                "name": game.name,
                "level": game.level
            }}
        return {"status": "failed", "message": "Game not found"}

    def update(self, game_id: str, data: dict) -> dict:
        game = self.repo.get_game_by_id(UUID(game_id))
        if game:
            game.name = data.get("name", game.name)
            game.level = data.get("level", game.level)
            self.repo.update_game(game)
            return {"status": "success", "message": f"Game {game.name} updated"}
        return {"status": "failed", "message": "Game not found"}

    def delete(self, game_id: str) -> dict:
        game = self.repo.get_game_by_id(UUID(game_id))
        if game:
            self.repo.delete_game(UUID(game_id))
            return {"status": "success", "message": f"Game {game_id} deleted"}
        return {"status": "failed", "message": "Game not found"}

    def start_game(self, game_id: str) -> dict:
        game = self.repo.get_game_by_id(UUID(game_id))
        if game and game.start_game():
            self.repo.save_game_state(game)
            return {"status": "success", "message": f"Game {game.name} started at {datetime.now()}"}
        return {"status": "failed", "message": "Cannot start game"}