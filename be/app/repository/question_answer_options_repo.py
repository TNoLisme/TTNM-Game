# app/repository/games/question_answer_options_repo.py
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.games.question_answer_options import QuestionAnswerOptions
from app.mapper.question_answer_options_mapper import QuestionAnswerOptionsMapper
from app.domain.games.question_answer_options import QuestionAnswerOptions as QuestionAnswerOptionsDomain
from typing import Optional, List
from .base_repo import BaseRepository

class QuestionAnswerOptionsRepository(BaseRepository[QuestionAnswerOptions, QuestionAnswerOptionsDomain]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, QuestionAnswerOptions, QuestionAnswerOptionsMapper)

    def get_by_question_id(self, question_id: str) -> Optional[QuestionAnswerOptionsDomain]:
        model = self.db_session.query(self.model_class).filter(self.model_class.question_id == question_id).first()
        return self.mapper_class.to_domain(model)

    def get_by_content_id(self, content_id: str) -> Optional[QuestionAnswerOptionsDomain]:
        model = self.db_session.query(self.model_class).filter(self.model_class.content_id == content_id).first()
        return self.mapper_class.to_domain(model)

    def get_all_by_game_id(self, game_id: str) -> List[QuestionAnswerOptionsDomain]:
        models = self.db_session.query(self.model_class).join(QuestionAnswerOptions.questions).filter(QuestionAnswerOptions.questions.game_id == game_id).all()
        return [self.mapper_class.to_domain(model) for model in models]