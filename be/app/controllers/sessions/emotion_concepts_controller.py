from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.repository.emotion_concepts_repo import EmotionConceptRepository


router = APIRouter(prefix="/emotions", tags=["Emotions"])


@router.get("/concepts")
async def list_emotion_concepts(db: Session = Depends(get_db)):
    """Trả về danh sách thẻ học cảm xúc (video/ảnh) từ database."""

    try:
        repo = EmotionConceptRepository(db)
        concepts = repo.get_all_emotion_concepts()

        payload = []
        for concept in concepts:
            payload.append(
                {
                    "concept_id": str(concept.concept_id),
                    "emotion": concept.emotion,
                    "level": concept.level,
                    "title": concept.title,
                    "video_path": concept.video_path,
                    "image_path": concept.image_path,
                    "audio_path": concept.audio_path,
                    "description": concept.description,
                }
            )

        return {"status": "success", "data": {"concepts": payload}}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error listing emotion concepts: {e}")
        raise HTTPException(500, detail="Không thể tải dữ liệu học cảm xúc từ database")
