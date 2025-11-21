from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.games.game_service import GameService
from app.services.analytics.child_progress_service import ChildProgressService
from uuid import UUID
from app.repository.sessions_repo import SessionsRepository
from app.services.sessions.sessions_service import SessionsService
from app.repository.games_repo import GamesRepository
from app.repository.child_progress_repo import ChildProgressRepository
from app.services.games.game_play_service import GamePlayService
from app.schemas.games.game_schema import GameSchema
from pydantic import BaseModel
from typing import List, Any, Dict
router = APIRouter(prefix="/games", tags=["games"])

class StartGameRequest(BaseModel):
    user_id: UUID
    level: int

# (Schema cho end-level)
class AnswerResult(BaseModel):
    question_id: UUID
    answer: str
    is_correct: bool
    response_time_ms: int

class EndLevelRequest(BaseModel):
    session_id: UUID
    results: List[AnswerResult]

# 1. Lấy tất cả game
@router.get("/")
async def get_all_games(db: Session = Depends(get_db)):
    repo = GamesRepository(db)
    service = GameService(repo)
    result = service.get_all_games()
    return result

# 2. Lấy thông tin game theo ID
@router.get("/{game_id}")
async def get_game_by_id(game_id: UUID, db: Session = Depends(get_db)):
    game_repo = GamesRepository(db)
    game_service = GameService(game_repo)
    game = game_service.get_by_id(game_id)
    if game["status"] != "success":
        raise HTTPException(status_code=404, detail="Game not found")
    return game["data"]

# 3. Lấy tiến trình hiện tại của user cho game
@router.get("/progress/{game_id}")
async def get_game_progress(game_id: UUID, db: Session = Depends(get_db), user_id: UUID = Query(...)):
    """
    Lấy tiến trình (progress) đã lưu của user cho một game cụ thể.
    Bao gồm level hiện tại, score, và mảng ratio (tỷ lệ cảm xúc).
    """
    print(f"Fetching progress for user {user_id} and game {game_id}")
    progress_repo = ChildProgressRepository(db)
    progress_service = ChildProgressService(progress_repo)
    progress = progress_service.get_progress(user_id, game_id)
    if not progress:
        return None
    return progress

# 4. Bắt đầu game → tạo session
@router.post("/start/{game_id}")
async def start_game(
    game_id: UUID, 
    body: StartGameRequest, 
    db: Session = Depends(get_db)
):
    """
    Bắt đầu một phiên chơi (Logic chung).
    Chỉ tạo Session và trả về 10 câu hỏi đã format.
    """
    service = GamePlayService(db)
    try:
        result = service.start_session(
            game_id=str(game_id), 
            level=body.level, 
            user_id=str(body.user_id)
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"[ERROR] Start Game (Generic) {game_id}: {e}")
        raise HTTPException(status_code=500, detail="Lỗi máy chủ khi bắt đầu game")


@router.post("/end-level") # <-- ENDPOINT MỚI
async def end_level(body: EndLevelRequest, db: Session = Depends(get_db)):
    """
    Kết thúc một level.
    Nhận mảng kết quả từ FE, lưu tất cả 'session_questions',
    cập nhật 'session' (điểm, lỗi), và cập nhật 'child_progress'.
    """
    service = GamePlayService(db)
    try:
        # Chuyển đổi Pydantic model sang List[Dict]
        results_list = [r.model_dump() for r in body.results]
        
        result = service.end_session_and_update_progress(
            session_id=body.session_id, 
            results=results_list
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"[ERROR] End Level (Generic) {body.session_id}: {e}")
        raise HTTPException(status_code=500, detail="Lỗi khi kết thúc level")