from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import Optional, TypeVar, Generic, List, Type

T = TypeVar('T')  # Generic type for model
D = TypeVar('D')  # Generic type for domain entity

class BaseRepository(ABC, Generic[T, D]):
    def __init__(self, db_session: Session, model_class: Type[T], mapper_class):
        self.db_session = db_session
        self.model_class = model_class
        self.mapper_class = mapper_class

    def create(self, domain_entity: D) -> D:
        model = self.mapper_class.to_model(domain_entity)
        self.db_session.add(model)
        self.db_session.commit()
        return self.mapper_class.to_domain(model)

    def get_by_id(self, entity_id: any) -> Optional[D]:
        model = self.db_session.query(self.model_class).filter(self.model_class.user_id == entity_id).first()
        return self.mapper_class.to_domain(model) if model else None

    def update(self, domain_entity: D) -> Optional[D]:
        model = self.db_session.query(self.model_class).filter(self.model_class.user_id == domain_entity.user_id).first()
        if model:
            updated_model = self.mapper_class.to_model(domain_entity)
            self.db_session.commit()
        return self.mapper_class.to_domain(model) if model else None

    def delete(self, entity_id: any) -> bool:
        model = self.db_session.query(self.model_class).filter(self.model_class.id == entity_id).first()
        if model:
            self.db_session.delete(model)
            self.db_session.commit()
            return True
        return False

    def get_all(self) -> List[D]:
        pass  # Abstract method to be implemented by specific repositories if needed