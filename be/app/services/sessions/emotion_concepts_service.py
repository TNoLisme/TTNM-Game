from uuid import UUID
from typing import Dict, List, Optional

from app.domain.sessions.emotion_concept import EmotionConcept as DomainEmotionConcept
from app.repository.emotion_concepts_repo import EmotionConceptRepository


class EmotionConceptsService:
    def __init__(self, db):
        self.repo = EmotionConceptRepository(db)

    def create_concept(self, data: dict) -> Dict:
        concept = DomainEmotionConcept(
            concept_id=data.get("concept_id"),
            emotion=data["emotion"],
            level=data["level"],
            title=data["title"],
            video_path=data.get("video_path"),
            image_path=data.get("image_path"),
            audio_path=data.get("audio_path"),
            description=data.get("description")
        )
        saved = self.repo.create_concept(concept)
        return {
            "status": "success",
            "message": f"Emotion concept {saved.title} created",
            "concept_id": str(saved.concept_id)
        }

    def get_concept(self, concept_id: UUID) -> Dict:
        concept = self.repo.get_concept_by_id(concept_id)
        if not concept:
            return {"status": "failed", "message": "Concept not found"}
        return {"status": "success", "data": self._to_dict(concept)}

    def get_all_concepts(self) -> Dict[str, Dict[int, List[Dict]]]:
        """
        Lấy tất cả thẻ học, group theo emotion và level.
        Format để FE có thể dùng trực tiếp.
        """
        concepts = self.repo.get_all_emotion_concepts()
        result: Dict[str, Dict[int, List[Dict]]] = {}

        for c in concepts:
            if c.emotion not in result:
                result[c.emotion] = {}
            if c.level not in result[c.emotion]:
                result[c.emotion][c.level] = []

            result[c.emotion][c.level].append(self._to_dict(c))

        return result

    def update_concept(self, concept_id: UUID, data: dict) -> Dict:
        existing = self.repo.get_concept_by_id(concept_id)
        if not existing:
            return {"status": "failed", "message": "Concept not found"}

        # Cập nhật các trường
        existing.emotion = data.get("emotion", existing.emotion)
        existing.level = data.get("level", existing.level)
        existing.title = data.get("title", existing.title)
        existing.video_path = data.get("video_path", existing.video_path)
        existing.image_path = data.get("image_path", existing.image_path)
        existing.audio_path = data.get("audio_path", existing.audio_path)
        existing.description = data.get("description", existing.description)

        updated = self.repo.update_concept(existing)
        return {"status": "success", "message": f"Concept {updated.title} updated"}

    def delete_concept(self, concept_id: UUID) -> Dict:
        success = self.repo.delete_concept(concept_id)
        if success:
            return {"status": "success", "message": f"Concept {concept_id} deleted"}
        return {"status": "failed", "message": "Concept not found"}

    def _to_dict(self, c: DomainEmotionConcept) -> Dict:
        return {
            "concept_id": str(c.concept_id),
            "emotion": c.emotion,
            "level": c.level,
            "title": c.title,
            "video_path": c.video_path,
            "image_path": c.image_path,
            "audio_path": c.audio_path,
            "description": c.description
        }
