from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID, uuid4

from app.domain.sessions.emotion_concept import EmotionConcept as DomainEmotionConcept
from app.models.sessions.emotion_concept import EmotionConcept as ModelEmotionConcept


class EmotionConceptRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_concept(self, concept: DomainEmotionConcept) -> DomainEmotionConcept:
        concept.concept_id = uuid4()

        model = ModelEmotionConcept(
            concept_id=concept.concept_id,
            emotion=concept.emotion,
            level=concept.level,
            title=concept.title,
            video_path=concept.video_path,
            image_path=concept.image_path,
            audio_path=concept.audio_path,
            description=concept.description
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def get_concept_by_id(self, concept_id: UUID) -> Optional[DomainEmotionConcept]:
        record = (
            self.db.query(ModelEmotionConcept)
            .filter_by(concept_id=concept_id)
            .first()
        )
        return self._to_domain(record) if record else None

    def get_all_emotion_concepts(self) -> List[DomainEmotionConcept]:
        records = self.db.query(ModelEmotionConcept).all()
        return [self._to_domain(r) for r in records]

    def get_by_emotion_and_level(self, emotion: str, level: int) -> Optional[DomainEmotionConcept]:
        record = (
            self.db.query(ModelEmotionConcept)
            .filter_by(emotion=emotion, level=level)
            .first()
        )
        return self._to_domain(record) if record else None

    def update_concept(self, concept: DomainEmotionConcept) -> DomainEmotionConcept:
        record = (
            self.db.query(ModelEmotionConcept)
            .filter_by(concept_id=concept.concept_id)
            .first()
        )
        if not record:
            raise ValueError(f"EmotionConcept {concept.concept_id} not found for update")

        record.emotion = concept.emotion
        record.level = concept.level
        record.title = concept.title
        record.video_path = concept.video_path
        record.image_path = concept.image_path
        record.audio_path = concept.audio_path
        record.description = concept.description

        self.db.commit()
        self.db.refresh(record)
        return self._to_domain(record)

    def update_video_path(self, concept_id: UUID, new_path: str) -> Optional[DomainEmotionConcept]:
        """
        Cập nhật riêng trường video_path cho 1 emotion concept.
        """
        record = (
            self.db.query(ModelEmotionConcept)
            .filter_by(concept_id=concept_id)
            .first()
        )
        if not record:
            return None

        record.video_path = new_path
        self.db.commit()
        self.db.refresh(record)
        return self._to_domain(record)

    def delete_concept(self, concept_id: UUID) -> bool:
        record = (
            self.db.query(ModelEmotionConcept)
            .filter_by(concept_id=concept_id)
            .first()
        )
        if not record:
            return False

        self.db.delete(record)
        self.db.commit()
        return True

    def _to_domain(self, record: ModelEmotionConcept) -> Optional[DomainEmotionConcept]:
        if not record:
            return None
        return DomainEmotionConcept(
            concept_id=record.concept_id,
            emotion=record.emotion,
            level=record.level,
            title=record.title,
            video_path=record.video_path,
            image_path=record.image_path,
            audio_path=record.audio_path,
            description=record.description
        )
