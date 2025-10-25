from uuid import UUID
from sqlalchemy.orm import Session
from models.games import Question as QuestionModel
from mapper.questions_mapper import QuestionsMapper
from domain.games.question import Question
import random
from .base_repo import BaseRepository

class QuestionsRepository(BaseRepository[QuestionModel, Question]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, QuestionModel, QuestionsMapper)

    def get_random_contents(self, game_id: UUID, level: int, count: int) -> list[Question]:
        question_models = self.db_session.query(self.model_class).filter(
            self.model_class.game_id == game_id, self.model_class.level == level
        ).all()
        if len(question_models) < count:
            raise ValueError("Not enough questions")
        selected_models = random.sample(question_models, count)
        return [self.mapper_class.to_domain(model) for model in selected_models]