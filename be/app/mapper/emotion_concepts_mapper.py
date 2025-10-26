from uuid import UUID
from app.models.sessions.emotion_concept import EmotionConcept as EmotionConceptModel
from app.domain.sessions.emotion_concept import EmotionConcept
from app.schemas.sessions.emotion_concept_schema import EmotionConceptSchema  # Giả định schema

class EmotionConceptsMapper:
    @staticmethod
    def to_domain(emotion_concept_model: EmotionConceptModel) -> EmotionConcept:
        """Chuyển đổi từ model sang domain entity."""
        if not emotion_concept_model:
            return None
        return EmotionConcept(
            concept_id=emotion_concept_model.concept_id,
            emotion=emotion_concept_model.emotion,
            level=emotion_concept_model.level,
            title=emotion_concept_model.title,
            video_path=emotion_concept_model.video_path,
            image_path=emotion_concept_model.image_path,
            audio_path=emotion_concept_model.audio_path,
            description=emotion_concept_model.description
        )

    @staticmethod
    def to_model(emotion_concept_domain: EmotionConcept) -> EmotionConceptModel:
        """Chuyển đổi từ domain entity sang model."""
        if not emotion_concept_domain:
            return None
        return EmotionConceptModel(
            concept_id=emotion_concept_domain.concept_id,
            emotion=emotion_concept_domain.emotion,
            level=emotion_concept_domain.level,
            title=emotion_concept_domain.title,
            video_path=emotion_concept_domain.video_path,
            image_path=emotion_concept_domain.image_path,
            audio_path=emotion_concept_domain.audio_path,
            description=emotion_concept_domain.description
        )

    @staticmethod
    def to_response(emotion_concept_model: EmotionConceptModel) -> EmotionConceptSchema.EmotionConceptResponse:
        """Chuyển đổi từ model sang response schema."""
        if not emotion_concept_model:
            return None
        return EmotionConceptSchema.EmotionConceptResponse(
            concept_id=emotion_concept_model.concept_id,
            emotion=emotion_concept_model.emotion,
            level=emotion_concept_model.level,
            title=emotion_concept_model.title,
            video_path=emotion_concept_model.video_path,
            image_path=emotion_concept_model.image_path,
            audio_path=emotion_concept_model.audio_path,
            description=emotion_concept_model.description
        )