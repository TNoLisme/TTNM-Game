from fastapi import APIRouter, Depends, HTTPException
from app.services.games.cv_service import CVService
from app.repository.games_repo import GamesRepository
from app.repository.game_contents_repo import GameContentsRepository
from app.repository.sessions_repo import SessionsRepository
from app.repository.session_questions_repo import SessionQuestionsRepository
from app.schemas.games.cv_schema import (
    ScenariosResponse, ScenarioResponse, StartSessionRequest, StartSessionResponse,
    SaveResultRequest, SaveResultResponse
)
from app.database import get_db
from uuid import UUID

router = APIRouter(prefix="/games/cv", tags=["Game CV"])


@router.get("/scenarios", response_model=ScenariosResponse)
async def get_scenarios(db=Depends(get_db)):
    """Lấy danh sách 6 tình huống cho game CV."""
    try:
        games_repo = GamesRepository(db)
        game_contents_repo = GameContentsRepository(db)
        sessions_repo = SessionsRepository(db)
        session_questions_repo = SessionQuestionsRepository(db)
        
        service = CVService(games_repo, game_contents_repo, sessions_repo, session_questions_repo)
        scenarios = service.get_scenarios()
        
        # Convert to ScenarioResponse format
        scenario_responses = [
            ScenarioResponse(
                id=scenario["id"],
                title=scenario["title"],
                description=scenario["description"],
                target_emotion=scenario["target_emotion"],
                instruction=scenario["instruction"],
                hint=scenario.get("hint"),
                image_path=scenario.get("image_path"),
                explanation=scenario.get("explanation")
            )
            for scenario in scenarios
        ]
        
        return {"scenarios": scenario_responses}
    except Exception as e:
        import traceback
        print(f"ERROR in get_scenarios: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy scenarios: {str(e)}")


@router.post("/start", response_model=StartSessionResponse)
async def start_session(request: StartSessionRequest, db=Depends(get_db)):
    """Khởi tạo session cho game CV."""
    try:
        games_repo = GamesRepository(db)
        game_contents_repo = GameContentsRepository(db)
        sessions_repo = SessionsRepository(db)
        session_questions_repo = SessionQuestionsRepository(db)
        
        service = CVService(games_repo, game_contents_repo, sessions_repo, session_questions_repo)
        result = service.start_session(request.user_id, request.game_type)
        
        return StartSessionResponse(
            session_id=UUID(result["session_id"]),
            message=result["message"]
        )
    except Exception as e:
        import traceback
        print(f"ERROR in start_session: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Lỗi khi khởi tạo session: {str(e)}")


@router.post("/result", response_model=SaveResultResponse)
async def save_result(request: SaveResultRequest, db=Depends(get_db)):
    """Lưu kết quả của một bài."""
    games_repo = GamesRepository(db)
    game_contents_repo = GameContentsRepository(db)
    sessions_repo = SessionsRepository(db)
    session_questions_repo = SessionQuestionsRepository(db)
    
    service = CVService(games_repo, game_contents_repo, sessions_repo, session_questions_repo)
    result = service.save_result(
        request.session_id,
        request.scenario_id,
        request.target_emotion,
        request.detected_emotion,
        request.success,
        request.time_taken
    )
    
    if result.get("status") != "success":
        raise HTTPException(status_code=400, detail=result.get("message"))
    
    return SaveResultResponse(message=result["message"])

