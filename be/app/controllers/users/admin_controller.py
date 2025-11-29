from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from app.services.users.admin_service import AdminService
from app.repository.admin_repo import AdminRepository
from app.repository.emotion_concepts_repo import EmotionConceptRepository
from app.repository.questions_repo import QuestionsRepository
from app.repository.game_contents_repo import GameContentsRepository as GameContentRepo
from app.database import get_db
from app.middleware.auth_middleware import require_admin
from pydantic import BaseModel
from typing import Optional, List
import shutil
import os
from pathlib import Path

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
    password: Optional[str] = None

class CreateUserRequest(BaseModel):
    username: str
    email: str
    name: str
    role: str
    password: str
    age: Optional[int] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    phone_number: Optional[str] = None
    report_preferences: Optional[str] = "weekly"

class CreateEmotionRequest(BaseModel):
    emotion: str
    level: int
    title: str
    video_path: Optional[str] = None
    image_path: Optional[str] = None
    audio_path: Optional[str] = None
    description: Optional[str] = None

class UpdateEmotionRequest(BaseModel):
    emotion: Optional[str] = None
    level: Optional[int] = None
    title: Optional[str] = None
    video_path: Optional[str] = None
    image_path: Optional[str] = None
    audio_path: Optional[str] = None
    description: Optional[str] = None

class CreateQuestionRequest(BaseModel):
    game_id: str  # Will be converted to UUID
    level: int
    content_id: str  # Will be converted to UUID
    correct_answer: str

class UpdateQuestionRequest(BaseModel):
    level: Optional[int] = None
    content_id: Optional[str] = None
    correct_answer: Optional[str] = None

class CreateGameContentRequest(BaseModel):
    game_id: str  # Will be converted to UUID
    level: int
    content_type: str
    media_path: Optional[str] = None
    question_text: Optional[str] = None
    correct_answer: Optional[str] = None
    emotion: Optional[str] = None
    explanation: Optional[str] = None

class UpdateGameContentRequest(BaseModel):
    level: Optional[int] = None
    content_type: Optional[str] = None
    media_path: Optional[str] = None
    question_text: Optional[str] = None
    correct_answer: Optional[str] = None
    emotion: Optional[str] = None
    explanation: Optional[str] = None

# ==================== Helper to create service ====================
def get_admin_service(db: Session) -> AdminService:
    admin_repo = AdminRepository(db)
    emotion_repo = EmotionConceptRepository(db)
    question_repo = QuestionsRepository(db)
    game_content_repo = GameContentRepo(db)
    return AdminService(admin_repo, emotion_repo, question_repo, game_content_repo)

# ==================== User Management Endpoints ====================
@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Lấy danh sách tất cả users với pagination"""
    service = get_admin_service(db)
    result = service.get_all_users(skip, limit)
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.post("/users")
async def create_user(request: CreateUserRequest, db: Session = Depends(get_db)):
    """Tạo user mới"""
    service = get_admin_service(db)
    result = service.create_user(request.dict())

    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])

    return result

@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Lấy thông tin chi tiết của một user"""
    service = get_admin_service(db)
    result = service.get_user_by_id(user_id)
    
    if result["status"] != "success":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result

@router.put("/users/{user_id}")
async def update_user(
    user_id: UUID,
    request: UpdateUserRequest,
    db: Session = Depends(get_db)
):
    """Cập nhật thông tin user"""
    service = get_admin_service(db)
    result = service.update_user(user_id, request.dict(exclude_unset=True))
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Xóa user"""
    service = get_admin_service(db)
    result = service.delete_user(user_id)
    
    if result["status"] != "success":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result

@router.get("/users/search")
async def search_users(
    name: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Tìm kiếm users theo tên"""
    service = get_admin_service(db)
    result = service.search_users(name, skip, limit)
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.get("/children")
async def list_children(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Lấy danh sách tất cả children"""
    service = get_admin_service(db)
    result = service.get_all_children(skip, limit)
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.get("/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Lấy thống kê tổng quan cho dashboard"""
    try:
        service = get_admin_service(db)
        
        # Lấy tất cả users
        users_result = service.get_all_users(skip=0, limit=10000)
        
        if users_result["status"] != "success":
            raise HTTPException(status_code=400, detail="Không thể lấy dữ liệu users")
        
        users = users_result["data"]["users"]
        
        # Đếm emotions - lấy từ tất cả levels
        emotion_repo = EmotionConceptRepository(db)
        total_emotions = 0
        try:
            for level in range(1, 11):
                emotions_result = emotion_repo.get_by_level(level)
                if emotions_result:
                    total_emotions += len(emotions_result)
        except:
            total_emotions = 0
        
        # Đếm questions - iterate through all games and levels
        game_content_repo = GameContentRepo(db)
        question_repo = QuestionsRepository(db)
        total_questions = 0
        
        try:
            for game_num in range(1, 7):  # 6 games
                game_uuid = UUID(int=game_num)
                for level in range(1, 11):  # 10 levels
                    contents = game_content_repo.get_game_content_by_level(game_uuid, level)
                    if contents:
                        # Get content_ids and fetch questions
                        content_ids = [content.content_id for content in contents]
                        if content_ids:
                            questions = question_repo.get_by_question_ids(content_ids)
                            total_questions += len(questions)
        except Exception as e:
            print(f"Error counting questions: {e}")
            total_questions = 0
        
        # Đếm active users (nếu có field status)
        total_active = len([u for u in users if u.get("status") == "active"])
        
        return {
            "status": "success",
            "data": {
                "total_users": len(users),
                "total_emotions": total_emotions,
                "total_questions": total_questions,
                "total_active": total_active
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy thống kê: {str(e)}")

# ==================== Emotion Concepts Management ====================
@router.get("/emotions")
async def list_emotions(
    level: Optional[int] = Query(None, ge=1, le=10),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Lấy danh sách emotion concepts"""
    emotion_repo = EmotionConceptRepository(db)
    
    try:
        all_emotions = []
        
        if level:
            # Lấy theo level cụ thể
            emotions = emotion_repo.get_by_level(level)
            if emotions:
                all_emotions = emotions
        else:
            # Lấy tất cả emotions
            for lvl in range(1, 11):
                emotions = emotion_repo.get_by_level(lvl)
                if emotions:
                    all_emotions.extend(emotions)
        
        # Apply pagination
        total = len(all_emotions)
        emotions_paginated = all_emotions[skip:skip+limit]
        
        # Convert to dict
        emotions_dict = [
            {
                "concept_id": str(e.concept_id),
                "emotion": e.emotion,
                "level": e.level,
                "title": e.title,
                "video_path": e.video_path,
                "image_path": e.image_path,
                "audio_path": e.audio_path,
                "description": e.description
            }
            for e in emotions_paginated
        ]
        
        return {
            "status": "success",
            "data": {
                "emotions": emotions_dict,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/emotions")
async def create_emotion(
    request: CreateEmotionRequest,
    db: Session = Depends(get_db)
):
    """Tạo emotion concept mới"""
    service = get_admin_service(db)
    result = service.create_emotion_concept(request.dict())
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.put("/emotions/{concept_id}")
async def update_emotion(
    concept_id: UUID,
    request: UpdateEmotionRequest,
    db: Session = Depends(get_db)
):
    """Cập nhật emotion concept"""
    service = get_admin_service(db)
    result = service.update_emotion_concept(concept_id, request.dict(exclude_unset=True))
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.delete("/emotions/{concept_id}")
async def delete_emotion(
    concept_id: UUID,
    db: Session = Depends(get_db)
):
    """Xóa emotion concept"""
    service = get_admin_service(db)
    result = service.delete_emotion_concept(concept_id)
    
    if result["status"] != "success":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result

# ==================== Game Content Management ====================
@router.get("/game_contents")
async def list_game_contents(
    game_id: Optional[str] = Query(None),
    level: Optional[int] = Query(None, ge=1, le=10),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Lấy danh sách game contents với filter"""
    game_content_repo = GameContentRepo(db)
    
    try:
        all_contents = []
        
        if game_id and level:
            # Lấy theo game_id và level cụ thể
            try:
                game_uuid = UUID(game_id)
                contents = game_content_repo.get_game_content_by_level(game_uuid, level)
                if contents:
                    all_contents = contents
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid game_id format")
        elif game_id:
            # Chỉ có game_id
            try:
                game_uuid = UUID(game_id)
                for lvl in range(1, 11):
                    contents = game_content_repo.get_game_content_by_level(game_uuid, lvl)
                    if contents:
                        all_contents.extend(contents)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid game_id format")
        else:
            # Lấy tất cả
            for g_id in range(1, 7):  # 6 games
                game_uuid = UUID(int=g_id)
                for lvl in range(1, 11):  # 10 levels
                    contents = game_content_repo.get_game_content_by_level(game_uuid, lvl)
                    if contents:
                        all_contents.extend(contents)
        
        # Apply pagination
        total = len(all_contents)
        contents_paginated = all_contents[skip:skip+limit]
        
        # Convert domain objects to dict
        contents_dict = [
            {
                "content_id": str(c.content_id),
                "game_id": str(c.game_id),
                "level": c.level,
                "content_type": c.content_type,
                "media_path": c.media_path,
                "question_text": c.question_text,
                "correct_answer": c.correct_answer,
                "emotion": c.emotion,
                "explanation": c.explanation
            }
            for c in contents_paginated
        ]
        
        return {
            "status": "success",
            "data": {
                "contents": contents_dict,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/game_contents")
async def create_game_content(
    request: CreateGameContentRequest,
    db: Session = Depends(get_db)
):
    """Tạo game content mới"""
    service = get_admin_service(db)
    
    # Convert string IDs to proper format and add content_id
    content_data = request.dict()
    content_data['content_id'] = uuid4()
    
    result = service.create_game_content(content_data)
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    # Nếu có correct_answer, tự động tạo question
    if request.correct_answer:
        try:
            question_data = {
                "game_id": request.game_id,
                "level": request.level,
                "content_id": str(content_data['content_id']),
                "correct_answer": request.correct_answer
            }
            service.create_question(question_data)
        except Exception as e:
            print(f"Warning: Could not create question: {str(e)}")
    
    return result

@router.put("/game_contents/{content_id}")
async def update_game_content(
    content_id: UUID,
    request: UpdateGameContentRequest,
    db: Session = Depends(get_db)
):
    """Cập nhật game content"""
    service = get_admin_service(db)
    result = service.update_game_content(content_id, request.dict(exclude_unset=True))
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.delete("/game_contents/{content_id}")
async def delete_game_content(
    content_id: UUID,
    db: Session = Depends(get_db)
):
    """Xóa game content"""
    service = get_admin_service(db)
    result = service.delete_game_content(content_id)
    
    if result["status"] != "success":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result

# ==================== Questions Management ====================
@router.get("/questions")
async def list_questions(
    game_id: Optional[str] = Query(None),
    level: Optional[int] = Query(None, ge=1, le=10),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Lấy danh sách câu hỏi với filter"""
    game_content_repo = GameContentRepo(db)
    question_repo = QuestionsRepository(db)
    
    try:
        all_questions = []
        
        if game_id and level:
            # Lấy theo game_id và level
            try:
                game_uuid = UUID(game_id)
                contents = game_content_repo.get_game_content_by_level(game_uuid, level)
                if contents:
                    content_ids = [c.content_id for c in contents]
                    all_questions = question_repo.get_by_question_ids(content_ids)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid game_id format")
        elif game_id:
            # Chỉ có game_id
            try:
                game_uuid = UUID(game_id)
                for lvl in range(1, 11):
                    contents = game_content_repo.get_game_content_by_level(game_uuid, lvl)
                    if contents:
                        content_ids = [c.content_id for c in contents]
                        questions = question_repo.get_by_question_ids(content_ids)
                        all_questions.extend(questions)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid game_id format")
        else:
            # Lấy tất cả
            for g_id in range(1, 7):
                game_uuid = UUID(int=g_id)
                for lvl in range(1, 11):
                    contents = game_content_repo.get_game_content_by_level(game_uuid, lvl)
                    if contents:
                        content_ids = [c.content_id for c in contents]
                        questions = question_repo.get_by_question_ids(content_ids)
                        all_questions.extend(questions)
        
        # Apply pagination
        total = len(all_questions)
        questions_paginated = all_questions[skip:skip+limit]
        
        # Convert domain objects to dict
        questions_dict = [
            {
                "question_id": str(q.question_id),
                "game_id": str(q.game_id),
                "level": q.level,
                "content_id": str(q.content.content_id) if q.content else None,
                "correct_answer": q.correct_answer,
                "content": {
                    "question_text": q.content.question_text,
                    "emotion": q.content.emotion,
                    "media_path": q.content.media_path,
                    "explanation": q.content.explanation
                } if q.content else None
            }
            for q in questions_paginated
        ]
        
        return {
            "status": "success",
            "data": {
                "questions": questions_dict,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/questions")
async def create_question(
    request: CreateQuestionRequest,
    db: Session = Depends(get_db)
):
    """Tạo câu hỏi mới"""
    service = get_admin_service(db)
    result = service.create_question(request.dict())
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.put("/questions/{question_id}")
async def update_question(
    question_id: UUID,
    request: UpdateQuestionRequest,
    db: Session = Depends(get_db)
):
    """Cập nhật câu hỏi"""
    service = get_admin_service(db)
    result = service.update_question(question_id, request.dict(exclude_unset=True))
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: UUID,
    db: Session = Depends(get_db)
):
    """Xóa câu hỏi"""
    service = get_admin_service(db)
    result = service.delete_question(question_id)
    
    if result["status"] != "success":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result

# ==================== File Upload Endpoint ====================
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload file (image/video/audio) và trả về path"""
    try:
        # Tạo thư mục upload nếu chưa có
        upload_dir = Path("fe/assets")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Tạo tên file unique
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid4()}.{file_extension}"
        file_path = upload_dir / unique_filename
        
        # Lưu file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Trả về path
        relative_path = f"/fe/assets/{unique_filename}"
        
        return {
            "status": "success",
            "data": {
                "file_path": relative_path,
                "filename": unique_filename
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")