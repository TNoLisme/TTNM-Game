from uuid import UUID
from domain.analytics.game_history import GameHistory
from repository.game_history_repo import GameHistoryRepository

class GameHistoryService:
    def __init__(self, game_history_repo: GameHistoryRepository):
        self.repo = game_history_repo

    def record_history(self, data: dict) -> dict:
        history = GameHistory(
            user_id=UUID(data.get("user_id")),
            session_id=UUID(data.get("session_id")),
            game_id=UUID(data.get("game_id")),
            score=data.get("score"),
            level=data.get("level")
        )
        self.repo.save_history(history)
        return {"status": "success", "message": f"Game history recorded for session {history.session_id}"}

    def get_history_by_user(self, user_id: UUID) -> dict:
        histories = self.repo.get_history_by_user(user_id)
        return {"status": "success", "data": [{"session_id": str(h.session_id), "score": h.score} for h in histories]} if histories else {"status": "failed", "message": "No history found"}