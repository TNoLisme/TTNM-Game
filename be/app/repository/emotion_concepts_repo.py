from uuid import UUID
from sqlalchemy.orm import Session
from app.models.sessions.emotion_concept import EmotionConcept as EmotionConceptModel
from app.domain.sessions.emotion_concept import EmotionConcept

class EmotionConceptRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_emotion_and_level(self, emotion: str, level: int) -> EmotionConcept | None:
        record = (
            self.db.query(EmotionConceptModel)
            .filter(
                EmotionConceptModel.emotion == emotion,
                EmotionConceptModel.level == level
            )
            .first()
        )

        if not record:
            return None

        return EmotionConcept(
            concept_id=record.concept_id,
            emotion=record.emotion,
            level=record.level,
            title=record.title,
            video_path=record.video_path,
            image_path=record.image_path,
            audio_path=record.audio_path,
            description=record.description
        )
