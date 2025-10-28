from uuid import UUID
from app.domain.sessions.emotion_concept import EmotionConcept
from app.repository.emotion_concepts_repo import GameContentsRepository

class EmotionConceptsService:
    def __init__(self, emotion_concepts_repo: GameContentsRepository):
        self.repo = emotion_concepts_repo

    def create_concept(self, data: dict) -> dict:
        concept = EmotionConcept(
            emotion=data.get("emotion"),
            level=data.get("level"),
            title=data.get("title"),
            video_path=data.get("video_path"),
            image_path=data.get("image_path"),
            audio_path=data.get("audio_path"),
            description=data.get("description")
        )
        self.repo.save_concept(concept)
        return {"status": "success", "message": f"Emotion concept {concept.title} created", "concept_id": str(concept.concept_id)}

    def get_concept(self, concept_id: UUID) -> dict:
        concept = self.repo.get_concept_by_id(concept_id)
        return {"status": "success", "data": {"title": concept.title, "emotion": concept.emotion}} if concept else {"status": "failed", "message": "Concept not found"}