from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.sessions import Session as SessionModel
from app.mapper.sessions_mapper import SessionsMapper
from app.domain.sessions.session import Session
from .base_repo import BaseRepository
from app.repository.questions_repo import QuestionsRepository

class SessionsRepository(BaseRepository[SessionModel, Session]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, SessionModel, SessionsMapper)
        self.questions_repo = QuestionsRepository(db_session)

    def get_by_id(self, session_id: UUID) -> Session | None:
        session_model = self.db_session.query(self.model_class) \
            .filter(self.model_class.session_id == session_id) \
            .first()
        return self.mapper_class.to_domain(session_model) if session_model else None

    def create(self, session: Session) -> Session:
        """Insert mới vào DB"""
        try:
            model = self.mapper_class.to_model(session)
            self.db_session.add(model)
            self.db_session.commit()
            self.db_session.refresh(model)
            return self.mapper_class.to_domain(model)
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"[SessionsRepository] Failed to create session: {e}")
            raise

    def update(self, session: Session) -> Session:
        """Update session đã tồn tại"""
        try:
            existing = self.db_session.query(self.model_class) \
                .filter(self.model_class.session_id == session.session_id) \
                .first()
            if not existing:
                raise ValueError(f"Session {session.session_id} không tồn tại để update.")

            model = self.mapper_class.to_model(session)
            for attr, value in model.__dict__.items():
                if attr.startswith("_"):
                    continue
                setattr(existing, attr, value)

            self.db_session.add(existing)
            self.db_session.commit()
            self.db_session.refresh(existing)
            return self.mapper_class.to_domain(existing)
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"[SessionsRepository] Failed to update session: {e}")
            raise
