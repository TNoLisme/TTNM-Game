# app/repository/questions_repo.py
from uuid import UUID, uuid4
from sqlalchemy.orm import Session, joinedload # <-- Đảm bảo có joinedload
from app.models.games import Question as QuestionModel
from app.mapper.questions_mapper import QuestionsMapper
from app.domain.games.question import Question
from app.domain.games.game_content import GameContent
from .base_repo import BaseRepository
from sqlalchemy.exc import IntegrityError
from typing import List


class QuestionsRepository(BaseRepository[QuestionModel, Question]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, QuestionModel, QuestionsMapper)
    
    # Lấy Question. Nếu chưa có, tạo mới.
    def get_or_create_by_content(self, content_domain: GameContent) -> Question:
        existing_model = self.db_session.query(self.model_class)\
            .options(joinedload(QuestionModel.content))\
            .filter(self.model_class.content_id == content_domain.content_id)\
            .first()
        
        if existing_model:
            return self.mapper_class.to_domain(existing_model)

        # Tạo mới
        new_question_domain = Question(
            question_id=uuid4(),
            game_id=content_domain.game_id,
            level=content_domain.level,
            content=content_domain,
            correct_answer=content_domain.correct_answer
        )
        new_question_model = self.mapper_class.to_model(new_question_domain)
        
        try:
            self.db_session.add(new_question_model)
            self.db_session.commit()
            self.db_session.refresh(new_question_model)
            

            # (Sau khi tạo, phải load lại model VỚI CONTENT)
            created_model = self.db_session.query(self.model_class)\
                .options(joinedload(QuestionModel.content))\
                .filter(self.model_class.question_id == new_question_model.question_id)\
                .first()
                
            return self.mapper_class.to_domain(created_model)
            
        except IntegrityError:
            self.db_session.rollback()
            existing_model = self.db_session.query(self.model_class)\
                .options(joinedload(QuestionModel.content))\
                .filter(self.model_class.content_id == content_domain.content_id)\
                .first()
            return self.mapper_class.to_domain(existing_model)

    # Lấy danh sách Question từ list các question_id
    def get_by_question_ids(self, question_ids: List[UUID]) -> List[Question]:
        if not question_ids:
            return []
            
        models = self.db_session.query(self.model_class)\
            .options(joinedload(QuestionModel.content)) \
            .filter(self.model_class.question_id.in_(question_ids))\
            .all()
            
        return [self.mapper_class.to_domain(model) for model in models]