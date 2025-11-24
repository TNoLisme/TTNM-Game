from uuid import UUID
from sqlalchemy.orm import Session
from app.models.sessions.emotion_concept import EmotionConcept as EmotionConceptModel
from app.domain.sessions.emotion_concept import EmotionConcept
from typing import List, Optional

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

    def get_by_level(self, level: int) -> List[EmotionConcept]:
        records = (
            self.db.query(EmotionConceptModel)
            .filter(EmotionConceptModel.level == level)
            .all()
        )
        
        return [
            EmotionConcept(
                concept_id=record.concept_id,
                emotion=record.emotion,
                level=record.level,
                title=record.title,
                video_path=record.video_path,
                image_path=record.image_path,
                audio_path=record.audio_path,
                description=record.description
            )
            for record in records
        ]

    def get_by_id(self, concept_id: UUID) -> Optional[EmotionConcept]:
        """Lấy emotion concept theo ID"""
        record = (
            self.db.query(EmotionConceptModel)
            .filter(EmotionConceptModel.concept_id == concept_id)
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

    def add(self, emotion: EmotionConcept) -> EmotionConcept:
        """Thêm emotion concept mới"""
        try:
            emotion_model = EmotionConceptModel(
                concept_id=emotion.concept_id,
                emotion=emotion.emotion,
                level=emotion.level,
                title=emotion.title,
                video_path=emotion.video_path,
                image_path=emotion.image_path,
                audio_path=emotion.audio_path,
                description=emotion.description
            )
            self.db.add(emotion_model)
            self.db.commit()
            self.db.refresh(emotion_model)
            
            return EmotionConcept(
                concept_id=emotion_model.concept_id,
                emotion=emotion_model.emotion,
                level=emotion_model.level,
                title=emotion_model.title,
                video_path=emotion_model.video_path,
                image_path=emotion_model.image_path,
                audio_path=emotion_model.audio_path,
                description=emotion_model.description
            )
        except Exception:
            self.db.rollback()
            raise

    def update(self, emotion: EmotionConcept) -> EmotionConcept:
        """Cập nhật emotion concept"""
        try:
            emotion_model = (
                self.db.query(EmotionConceptModel)
                .filter(EmotionConceptModel.concept_id == emotion.concept_id)
                .first()
            )
            
            if not emotion_model:
                raise ValueError(f"Emotion concept with id {emotion.concept_id} not found")
            
            # Update fields
            emotion_model.emotion = emotion.emotion
            emotion_model.level = emotion.level
            emotion_model.title = emotion.title
            emotion_model.video_path = emotion.video_path
            emotion_model.image_path = emotion.image_path
            emotion_model.audio_path = emotion.audio_path
            emotion_model.description = emotion.description
            
            self.db.commit()
            self.db.refresh(emotion_model)
            
            return EmotionConcept(
                concept_id=emotion_model.concept_id,
                emotion=emotion_model.emotion,
                level=emotion_model.level,
                title=emotion_model.title,
                video_path=emotion_model.video_path,
                image_path=emotion_model.image_path,
                audio_path=emotion_model.audio_path,
                description=emotion_model.description
            )
        except Exception:
            self.db.rollback()
            raise

    def delete(self, concept_id: UUID) -> bool:
        """Xóa emotion concept"""
        try:
            emotion = (
                self.db.query(EmotionConceptModel)
                .filter(EmotionConceptModel.concept_id == concept_id)
                .first()
            )
            
            if not emotion:
                return False
            
            self.db.delete(emotion)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise