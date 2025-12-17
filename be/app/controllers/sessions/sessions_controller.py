from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from uuid import UUID
from sqlalchemy import text
from app.database import get_db
from app.repository.sessions_repo import SessionsRepository

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/user/{user_id}/history")
async def get_user_session_history(user_id: UUID, skip: int = Query(0, ge=0), limit: int = Query(100, ge=1), db=Depends(get_db)):
    """Return session history for a user. Each item contains start_time, end_time, score, game_id, level."""
    try:
        repo = SessionsRepository(db)
        # Use repository method if exists, else raw query
        try:
            sessions = repo.get_by_user(str(user_id), skip=skip, limit=limit)
        except Exception:
            # Fallback raw query
            query = text("""
                SELECT s.session_id, s.user_id, s.game_id, s.start_time, s.end_time, s.score, s.level
                FROM sessions s
                WHERE s.user_id = :user_id
                ORDER BY s.start_time DESC
            """)
            result = db.execute(query, {"user_id": str(user_id)})
            sessions = []
            for row in result:
                sessions.append({
                    "session_id": str(row.session_id),
                    "game_id": str(row.game_id),
                    "start_time": row.start_time.isoformat() if row.start_time else None,
                    "end_time": row.end_time.isoformat() if row.end_time else None,
                    "score": int(row.score) if row.score is not None else 0,
                    "level": int(row.level) if row.level is not None else 1
                })

        # If repo returned domain objects, normalize them
        normalized = []
        for s in sessions:
            if isinstance(s, dict):
                normalized.append(s)
            else:
                # assume domain object with attributes
                normalized.append({
                    "session_id": str(getattr(s, 'session_id', '')),
                    "game_id": str(getattr(s, 'game_id', '')),
                    "start_time": getattr(s, 'start_time').isoformat() if getattr(s, 'start_time', None) else None,
                    "end_time": getattr(s, 'end_time').isoformat() if getattr(s, 'end_time', None) else None,
                    "score": int(getattr(s, 'score', 0)) if getattr(s, 'score', None) is not None else 0,
                    "level": int(getattr(s, 'level', 1))
                })

        return {"status": "success", "sessions": normalized}
    except Exception as e:
        print(f"[ERROR] get_user_session_history: {e}")
        raise HTTPException(status_code=500, detail=str(e))