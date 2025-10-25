from uuid import UUID
from sqlalchemy.orm import Session
from models.games import Game as GameModel
from mapper.games_mapper import GamesMapper
from domain.games.game import Game
from .base_repo import BaseRepository

class GamesRepository(BaseRepository[GameModel, Game]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, GameModel, GamesMapper)