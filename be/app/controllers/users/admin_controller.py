from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from app.services.users.admin_service import AdminService
from app.repository.admin_repo import AdminRepository
from app.repository.emotion_concepts_repo import GameContentsRepository
from app.repository.questions_repo import QuestionsRepository
from app.repository.game_contents_repo import GameContentsRepository as GameContentRepo
from app.database import get_db
from app.middleware.auth_middleware import require_admin
from pydantic import BaseModel
from typing import Optional

router = APIRouter(
    prefix="/admin",

    tags=["Admin"],
    dependencies=[Depends(require_admin)]
)

# ==================== Request Schemas ====================
class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

class CreateEmotionRequest(BaseModel):
    concept_id: str
    emotion: str
    level: int
    title: str
    video_path: str
    image_path: str
    audio_path: str
    description: str

class CreateQuestionRequest(BaseModel):
    game_id: str
    level: int
    content_id: str
    correct_answer: str

class CreateGameContentRequest(BaseModel):
    game_id: str
    level: int
    content_type: str
    media_path: str
    question_text: str
    correct_answer: str
    emotion: str
    explanation: str

# ==================== User Management Endpoints ====================
@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db=Depends(get_db)
):
    """Lấy danh sách tất cả users với pagination"""
    admin_repo = AdminRepository(db)
    emotion_repo = GameContentsRepository(db)
    question_repo = QuestionsRepository(db)
    game_content_repo = GameContentRepo(db)
    
    service = AdminService(admin_repo, emotion_repo, question_repo, game_content_repo)
    result = service.get_all_users(skip, limit)
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: UUID,
    db=Depends(get_db)
):
    """Lấy thông tin chi tiết của một user"""
    admin_repo = AdminRepository(db)
    emotion_repo = GameContentsRepository(db)
    question_repo = QuestionsRepository(db)
    game_content_repo = GameContentRepo(db)
    
    service = AdminService(admin_repo, emotion_repo, question_repo, game_content_repo)
    result = service.get_user_by_id(user_id)
    
    if result["status"] != "success":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result

@router.put("/users/{user_id}")
async def update_user(
    user_id: UUID,
    request: UpdateUserRequest,
    db=Depends(get_db)
):
    """Cập nhật thông tin user"""
    admin_repo = AdminRepository(db)
    emotion_repo = GameContentsRepository(db)
    question_repo = QuestionsRepository(db)
    game_content_repo = GameContentRepo(db)
    
    service = AdminService(admin_repo, emotion_repo, question_repo, game_content_repo)
    result = service.update_user(user_id, request.dict(exclude_unset=True))
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    db=Depends(get_db)
):
    """Xóa user"""
    admin_repo = AdminRepository(db)
    emotion_repo = GameContentsRepository(db)
    question_repo = QuestionsRepository(db)
    game_content_repo = GameContentRepo(db)
    
    service = AdminService(admin_repo, emotion_repo, question_repo, game_content_repo)
    result = service.delete_user(user_id)
    
    if result["status"] != "success":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result

@router.get("/children")
async def list_children(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db=Depends(get_db)
):
    """Lấy danh sách tất cả children"""
    admin_repo = AdminRepository(db)
    emotion_repo = GameContentsRepository(db)
    question_repo = QuestionsRepository(db)
    game_content_repo = GameContentRepo(db)
    
    service = AdminService(admin_repo, emotion_repo, question_repo, game_content_repo)
    result = service.get_all_children(skip, limit)
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.get("/users/search")
async def search_users(
    name: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db=Depends(get_db)
):
    """Tìm kiếm users theo tên"""
    admin_repo = AdminRepository(db)
    emotion_repo = GameContentsRepository(db)
    question_repo = QuestionsRepository(db)
    game_content_repo = GameContentRepo(db)
    
    service = AdminService(admin_repo, emotion_repo, question_repo, game_content_repo)
    result = service.search_users(name, skip, limit)
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

# ==================== Emotion Concepts Management ====================
@router.get("/emotions")
async def list_emotions(
    game_id: UUID = Query(...),
    level: int = Query(..., ge=1, le=10),
    db=Depends(get_db)
):
    """Lấy danh sách emotion concepts"""
    admin_repo = AdminRepository(db)
    emotion_repo = GameContentsRepository(db)
    question_repo = QuestionsRepository(db)
    game_content_repo = GameContentRepo(db)
    
    service = AdminService(admin_repo, emotion_repo, question_repo, game_content_repo)
    result = service.get_all_emotions(game_id, level)
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.post("/emotions")
async def create_emotion(
    request: CreateEmotionRequest,
    db=Depends(get_db)
):
    """Tạo emotion concept mới"""
    admin_repo = AdminRepository(db)
    emotion_repo = GameContentsRepository(db)
    question_repo = QuestionsRepository(db)
    game_content_repo = GameContentRepo(db)
    
    service = AdminService(admin_repo, emotion_repo, question_repo, game_content_repo)
    result = service.create_emotion_concept(request.dict())
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

# ==================== Questions Management ====================
@router.get("/questions")
async def list_questions(
    game_id: UUID = Query(...),
    level: int = Query(..., ge=1, le=10),
    count: int = Query(10, ge=1, le=100),
    db=Depends(get_db)
):
    """Lấy danh sách câu hỏi"""
    admin_repo = AdminRepository(db)
    emotion_repo = GameContentsRepository(db)
    question_repo = QuestionsRepository(db)
    game_content_repo = GameContentRepo(db)
    
    service = AdminService(admin_repo, emotion_repo, question_repo, game_content_repo)
    result = service.get_all_questions(game_id, level, count)
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.post("/questions")
async def create_question(
    request: CreateQuestionRequest,
    db=Depends(get_db)
):
    """Tạo câu hỏi mới"""
    admin_repo = AdminRepository(db)
    emotion_repo = GameContentsRepository(db)
    question_repo = QuestionsRepository(db)
    game_content_repo = GameContentRepo(db)
    
    service = AdminService(admin_repo, emotion_repo, question_repo, game_content_repo)
    result = service.create_question(request.dict())
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.put("/questions/{question_id}")
async def update_question(
    question_id: UUID,
    request: CreateQuestionRequest,
    db=Depends(get_db)
):
    """Cập nhật câu hỏi"""
    admin_repo = AdminRepository(db)
    emotion_repo = GameContentsRepository(db)
    question_repo = QuestionsRepository(db)
    game_content_repo = GameContentRepo(db)
    
    service = AdminService(admin_repo, emotion_repo, question_repo, game_content_repo)
    result = service.update_question(question_id, request.dict())
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: UUID,
    db=Depends(get_db)
):
    """Xóa câu hỏi"""
    admin_repo = AdminRepository(db)
    emotion_repo = GameContentsRepository(db)
    question_repo = QuestionsRepository(db)
    game_content_repo = GameContentRepo(db)
    
    service = AdminService(admin_repo, emotion_repo, question_repo, game_content_repo)
    result = service.delete_question(question_id)
    
    if result["status"] != "success":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result

# ==================== Game Content Management ====================
@router.get("/game-contents")
async def list_game_contents(
    game_id: UUID = Query(...),
    level: int = Query(..., ge=1, le=10),
    db=Depends(get_db)
):
    """Lấy danh sách game contents"""
    admin_repo = AdminRepository(db)
    emotion_repo = GameContentsRepository(db)
    question_repo = QuestionsRepository(db)
    game_content_repo = GameContentRepo(db)
    
    service = AdminService(admin_repo, emotion_repo, question_repo, game_content_repo)
    result = service.get_all_game_contents(game_id, level)
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.post("/game-contents")
async def create_game_content(
    request: CreateGameContentRequest,
    db=Depends(get_db)
):
    """Tạo game content mới"""
    admin_repo = AdminRepository(db)
    emotion_repo = GameContentsRepository(db)
    question_repo = QuestionsRepository(db)
    game_content_repo = GameContentRepo(db)
    
    service = AdminService(admin_repo, emotion_repo, question_repo, game_content_repo)
    result = service.create_game_content(request.dict())
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.put("/game-contents/{content_id}")
async def update_game_content(
    content_id: UUID,
    request: CreateGameContentRequest,
    db=Depends(get_db)
):
    """Cập nhật game content"""
    admin_repo = AdminRepository(db)
    emotion_repo = GameContentsRepository(db)
    question_repo = QuestionsRepository(db)
    game_content_repo = GameContentRepo(db)
    
    service = AdminService(admin_repo, emotion_repo, question_repo, game_content_repo)
    result = service.update_game_content(content_id, request.dict())
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.delete("/game-contents/{content_id}")
async def delete_game_content(
    content_id: UUID,
    db=Depends(get_db)
):
    """Xóa game content"""
    admin_repo = AdminRepository(db)
    emotion_repo = GameContentsRepository(db)
    question_repo = QuestionsRepository(db)
    game_content_repo = GameContentRepo(db)
    
    service = AdminService(admin_repo, emotion_repo, question_repo, game_content_repo)
    result = service.delete_game_content(content_id)
    
    if result["status"] != "success":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result