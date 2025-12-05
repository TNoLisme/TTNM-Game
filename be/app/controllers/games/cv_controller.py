from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.services.games.cv_service import CVService
from app.repository.games_repo import GamesRepository
from app.repository.game_contents_repo import GameContentsRepository
from app.repository.sessions_repo import SessionsRepository
from app.repository.session_questions_repo import SessionQuestionsRepository
from app.schemas.games.cv_schema import (
    ScenariosResponse, ScenarioResponse, StartSessionRequest, StartSessionResponse,
    SaveResultRequest, SaveResultResponse, EndSessionRequest, EndSessionResponse
)
from app.database import get_db
from uuid import UUID
import httpx

router = APIRouter(prefix="/games/cv", tags=["Game CV"])


@router.get("/scenarios", response_model=ScenariosResponse)
async def get_scenarios(level: int = 1, db=Depends(get_db)):
    """Lấy danh sách scenarios cho game CV, random 10 màn cho mỗi level."""
    try:
        games_repo = GamesRepository(db)
        game_contents_repo = GameContentsRepository(db)
        sessions_repo = SessionsRepository(db)
        session_questions_repo = SessionQuestionsRepository(db)
        
        service = CVService(games_repo, game_contents_repo, sessions_repo, session_questions_repo)
        scenarios = service.get_scenarios(level=level)
        
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
                explanation=scenario.get("explanation"),
                level=scenario.get("level", 1)
            )
            for scenario in scenarios
        ]
        
        return {"scenarios": scenario_responses}
    except Exception as e:
        import traceback
        print(f"ERROR in get_scenarios: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy scenarios: {str(e)}")


@router.get("/requests", response_model=ScenariosResponse)
async def get_requests(db=Depends(get_db)):
    """Lấy danh sách yêu cầu biểu cảm trực tiếp (không có tình huống)."""
    try:
        games_repo = GamesRepository(db)
        game_contents_repo = GameContentsRepository(db)
        sessions_repo = SessionsRepository(db)
        session_questions_repo = SessionQuestionsRepository(db)

        service = CVService(games_repo, game_contents_repo, sessions_repo, session_questions_repo)
        requests = service.get_requests()

        request_responses = [
            ScenarioResponse(
                id=request_item["id"],
                title=request_item["title"],
                description=request_item["description"],
                target_emotion=request_item["target_emotion"],
                instruction=request_item["instruction"],
                hint=request_item.get("hint"),
                image_path=request_item.get("image_path"),
                explanation=request_item.get("explanation"),
                level=request_item.get("level", 1),
            )
            for request_item in requests
        ]

        return {"scenarios": request_responses}
    except Exception as e:
        import traceback
        print(f"ERROR in get_requests: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy yêu cầu biểu cảm: {str(e)}")


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
    try:
        print(f"💾 Received save_result: session_id={request.session_id}, scenario_id={request.scenario_id}, success={request.success}")
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
            request.time_taken,
            request.confidence_score or 0.0,
            request.check_hint or False
        )
        
        print(f"💾 Save result response: {result.get('status')}")
        
        if result.get("status") != "success":
            raise HTTPException(status_code=400, detail=result.get("message"))

        return SaveResultResponse(message=result["message"])
    except Exception as e:
        import traceback
        print(f"ERROR in save_result endpoint: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Lỗi khi lưu kết quả: {str(e)}")


@router.post("/end", response_model=EndSessionResponse)
async def end_session(request: EndSessionRequest, db=Depends(get_db)):
    """Kết thúc session cho game CV."""
    try:
        print(f"📥 Received end_session request: session_id={request.session_id}")
        games_repo = GamesRepository(db)
        game_contents_repo = GameContentsRepository(db)
        sessions_repo = SessionsRepository(db)
        session_questions_repo = SessionQuestionsRepository(db)

        service = CVService(games_repo, game_contents_repo, sessions_repo, session_questions_repo)
        result = service.end_session(request.session_id)

        print(f"📤 End session response: status={result.get('status')}, score={result.get('score')}")

        if result.get("status") != "success":
            raise HTTPException(status_code=400, detail=result.get("message"))

        return EndSessionResponse(
            message=result["message"],
            session_id=UUID(result["session_id"]),
            score=result["score"],
            emotion_errors=result["emotion_errors"]
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"❌ ERROR in end_session: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Lỗi khi kết thúc session: {str(e)}")


@router.get("/emotion-scores")
async def get_emotion_scores(user_id: UUID, db=Depends(get_db)):
    """Lấy điểm cao nhất (accuracy %) của mỗi cảm xúc từ các session đã chơi game CV."""
    try:
        import json
        from app.models.sessions.session import Session as SessionModel
        from app.models.games.game import Game as GameModel
        
        # Tìm game CV
        cv_game = db.query(GameModel).filter(
            GameModel.game_type == "GameCV"
        ).first()
        
        if not cv_game:
            return {"scores": {}}
        
        # Lấy tất cả session đã kết thúc của user cho game CV
        sessions = db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.game_id == cv_game.game_id,
            SessionModel.state == "end"
        ).all()
        
        # Tính điểm cao nhất cho mỗi cảm xúc
        emotion_best_scores = {}
        
        print(f"📊 Processing {len(sessions)} sessions for user {user_id}")
        
        # Map tất cả các biến thể tên cảm xúc có thể có (bao gồm cả encoding sai)
        emotion_name_mapping = {
            "vui": "vui",
            "vui vẻ": "vui",
            "vui ve": "vui",
            "happy": "vui",
            "buồn": "buồn",
            "buồn bã": "buồn",
            "buon": "buồn",
            "buon ba": "buồn",
            "bu?n": "buồn",  # Encoding sai
            "bu?n bã": "buồn",  # Encoding sai
            "sad": "buồn",
            "ngạc nhiên": "ngạc nhiên",
            "ng?c nhiên": "ngạc nhiên",  # Encoding sai
            "ng?c nhi?n": "ngạc nhiên",  # Encoding sai
            "ngac nhien": "ngạc nhiên",
            "surprise": "ngạc nhiên",
            "tức giận": "tức giận",
            "t?c gi?n": "tức giận",  # Encoding sai - FIX
            "tức": "tức giận",
            "tuc gian": "tức giận",
            "tuc": "tức giận",
            "angry": "tức giận",
            "sợ hãi": "sợ hãi",
            "s? hãi": "sợ hãi",  # Encoding sai
            "s?": "sợ hãi",  # Encoding sai
            "sợ": "sợ hãi",
            "so hai": "sợ hãi",
            "so": "sợ hãi",
            "fear": "sợ hãi",
            "ghê tởm": "ghê tởm",
            "ghê": "ghê tởm",
            "gh? t?m": "ghê tởm",  # Encoding sai
            "ghe tom": "ghê tởm",
            "ghe": "ghê tởm",
            "disgust": "ghê tởm"
        }
        
        for session in sessions:
            if not session.emotion_errors:
                print(f"   Session {session.session_id}: No emotion_errors")
                continue
                
            emotion_errors = session.emotion_errors
            if isinstance(emotion_errors, str):
                try:
                    emotion_errors = json.loads(emotion_errors)
                except Exception as e:
                    print(f"   Session {session.session_id}: Error parsing emotion_errors JSON: {e}")
                    continue
            
            if not isinstance(emotion_errors, dict):
                print(f"   Session {session.session_id}: emotion_errors is not a dict")
                continue
            
            print(f"   Session {session.session_id}: emotion_errors = {emotion_errors}")
            
            # Lấy confidence score cao nhất cho mỗi cảm xúc trong session này
            for emotion, stats in emotion_errors.items():
                if isinstance(stats, dict) and "best_confidence" in stats:
                    best_confidence = float(stats.get("best_confidence", 0.0))
                    
                    if best_confidence > 0:
                        # Normalize và map emotion name
                        emotion_clean = emotion.strip() if emotion else ""
                        emotion_lower = emotion_clean.lower()
                        
                        # Map tên cảm xúc về tên chuẩn
                        emotion_normalized = emotion_name_mapping.get(emotion_lower, emotion_lower)
                        
                        # Đảm bảo emotion_normalized là một trong 6 cảm xúc chuẩn
                        valid_emotions = ["vui", "buồn", "ngạc nhiên", "tức giận", "sợ hãi", "ghê tởm"]
                        if emotion_normalized not in valid_emotions:
                            # Thử tìm trong valid_emotions bằng cách so sánh từng từ
                            found = False
                            for valid_emotion in valid_emotions:
                                # So sánh từng từ trong tên cảm xúc
                                emotion_words = emotion_lower.split()
                                valid_words = valid_emotion.split()
                                # Nếu có từ nào trùng thì map về cảm xúc đó
                                if any(word in valid_emotion for word in emotion_words) or \
                                   any(word in emotion_lower for word in valid_words):
                                    emotion_normalized = valid_emotion
                                    found = True
                                    print(f"      🔄 Mapped '{emotion}' -> '{emotion_normalized}' by word matching")
                                    break
                            
                            # Nếu vẫn không tìm thấy, thử match với encoding sai (t?c gi?n -> tức giận)
                            if not found:
                                # Thử replace ? với các ký tự có thể có
                                emotion_fixed = emotion_lower.replace("?c", "ức").replace("?n", "ần").replace("?", "ồ")
                                emotion_normalized = emotion_name_mapping.get(emotion_fixed, emotion_normalized)
                                if emotion_normalized in valid_emotions:
                                    found = True
                                    print(f"      🔄 Mapped '{emotion}' -> '{emotion_normalized}' by fixing encoding")
                            
                            if not found or emotion_normalized not in valid_emotions:
                                print(f"      ⚠️ Unknown emotion '{emotion}' ({emotion_lower}), skipping")
                                continue
                        
                        # Đảm bảo confidence trong khoảng 0-100
                        best_confidence = max(0.0, min(100.0, best_confidence))
                        
                        print(f"      Emotion '{emotion}' -> '{emotion_normalized}': best_confidence = {best_confidence:.2f}% (thang 100)")
                        
                        # Lưu điểm cao nhất (confidence score cao nhất, thang 100)
                        if emotion_normalized not in emotion_best_scores or best_confidence > emotion_best_scores[emotion_normalized]:
                            emotion_best_scores[emotion_normalized] = round(best_confidence, 2)
                            print(f"      ✅ New best confidence for {emotion_normalized}: {best_confidence:.2f}% (thang 100)")
        
        print(f"📊 Final emotion_best_scores: {emotion_best_scores}")
        
        # Đảm bảo trả về tất cả 6 cảm xúc, nếu không có thì trả về 0
        valid_emotions = ["vui", "buồn", "ngạc nhiên", "tức giận", "sợ hãi", "ghê tởm"]
        for emotion in valid_emotions:
            if emotion not in emotion_best_scores:
                emotion_best_scores[emotion] = 0.0
                print(f"   ⚠️ No score found for '{emotion}', defaulting to 0.0")
        
        print(f"📊 Final emotion_best_scores (with defaults): {emotion_best_scores}")
        return {"scores": emotion_best_scores}
    except Exception as e:
        import traceback
        print(f"ERROR in get_emotion_scores: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy điểm cảm xúc: {str(e)}")


@router.get("/completed-levels")
async def get_completed_levels(user_id: UUID, db=Depends(get_db)):
    """Lấy danh sách level đã hoàn thành cho game CV (GV1)."""
    try:
        from app.models.games.game import Game as GameModel
        from app.models.analytics.child_progress import ChildProgress as ChildProgressModel
        
        MAX_LEVEL = 6
        STAGES_PER_LEVEL = 10
        
        # Tìm game CV "tình huống" (không phải "yêu cầu")
        cv_games = db.query(GameModel).filter(
            GameModel.game_type == "GameCV"
        ).all()
        
        # Lọc game "tình huống" (không chứa "yêu cầu" trong tên)
        cv_game = None
        for game in cv_games:
            game_name_lower = game.name.lower() if game.name else ""
            if "yêu cầu" not in game_name_lower and "request" not in game_name_lower:
                cv_game = game
                break
        
        if not cv_game:
            # Fallback: lấy game CV đầu tiên
            cv_game = cv_games[0] if cv_games else None
        
        if not cv_game:
            return {
                "levels": [],
                "current_level": 1,
                "max_level": MAX_LEVEL
            }
        
        # Lấy tất cả child_progress của user cho game CV
        progress_records = db.query(ChildProgressModel).filter(
            ChildProgressModel.child_id == user_id,
            ChildProgressModel.game_id == cv_game.game_id
        ).all()
        
        # Tạo map level -> progress
        progress_map = {p.level: p for p in progress_records}
        
        # Build response
        levels = []
        current_level = 1
        
        for level in range(1, MAX_LEVEL + 1):
            if level in progress_map:
                progress = progress_map[level]
                score = progress.score if progress.score is not None else 0
                completed = (score >= STAGES_PER_LEVEL)
                
                levels.append({
                    "level": level,
                    "score": score,
                    "max_score": STAGES_PER_LEVEL,
                    "completed": completed,
                    "unlocked": True  # Nếu có trong progress thì đã unlock
                })
                
                # Nếu chưa completed thì đây là current_level
                if not completed and level >= current_level:
                    current_level = level
            else:
                # Level chưa unlock
                # Chỉ unlock level 1 mặc định, hoặc level tiếp sau level completed
                unlocked = (level == 1) or (level - 1 in progress_map and progress_map[level - 1].score >= STAGES_PER_LEVEL)
                
                levels.append({
                    "level": level,
                    "score": 0,
                    "max_score": STAGES_PER_LEVEL,
                    "completed": False,
                    "unlocked": unlocked
                })
        
        print(f"📊 User {user_id} progress:")
        for lvl in levels:
            status = "✅ completed" if lvl["completed"] else ("🔓 unlocked" if lvl["unlocked"] else "🔒 locked")
            print(f"   Level {lvl['level']}: {lvl['score']}/{lvl['max_score']} {status}")
        print(f"   Current level: {current_level}")
        
        return {
            "levels": levels,
            "current_level": current_level,
            "max_level": MAX_LEVEL
        }
    except Exception as e:
        import traceback
        print(f"ERROR in get_completed_levels: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy danh sách level đã hoàn thành: {str(e)}")


@router.get("/audio-proxy")
async def audio_proxy(url: str):
    """Proxy endpoint để tải audio từ FPT AI, tránh CORS issue. Cũng hỗ trợ JSON response khi poll."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0, follow_redirects=True)
            
            # Determine content type from response or URL
            content_type = response.headers.get("content-type", "")
            is_json = "json" in content_type.lower() or url.endswith(".json") or "api.fpt.ai" in url
            is_audio = "audio" in content_type.lower() or ".mp3" in url or "file01.fpt.ai" in url
            
            if response.status_code in [200, 206]:  # 206 is Partial Content for audio
                if is_json:
                    # Return JSON response
                    try:
                        json_data = response.json()
                        from fastapi.responses import JSONResponse
                        return JSONResponse(
                            content=json_data,
                            headers={
                                "Access-Control-Allow-Origin": "*",
                                "Content-Type": "application/json"
                            }
                        )
                    except:
                        # If not valid JSON, return as text
                        return JSONResponse(
                            content={"error": "Invalid JSON response"},
                            status_code=500
                        )
                else:
                    # Return audio file
                    return StreamingResponse(
                        iter([response.content]),
                        media_type="audio/mpeg",
                        headers={
                            "Access-Control-Allow-Origin": "*",
                            "Content-Type": "audio/mpeg",
                            "Accept-Ranges": "bytes"
                        }
                    )
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch resource")
    except Exception as e:
        print(f"Error in audio proxy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi khi tải resource: {str(e)}")

