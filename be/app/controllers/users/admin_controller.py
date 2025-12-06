from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from uuid import UUID
from app.services.users.admin_service import AdminService
from app.repository.admin_repo import AdminRepository
from app.repository.users_repo import UsersRepository
from app.repository.child_repo import ChildRepository
from app.repository.emotion_concepts_repo import EmotionConceptRepository
from app.repository.questions_repo import QuestionsRepository
from app.repository.game_contents_repo import GameContentsRepository as GameContentRepo
from app.database import get_db
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import os
import shutil
from pathlib import Path

router = APIRouter(prefix="/admin", tags=["Admin"])

# ==================== Request Schemas ====================
class CreateUserRequest(BaseModel):
    username: str
    name: str
    email: EmailStr
    password: str
    role: str  # 'admin' or 'child'
    age: Optional[int] = None
    gender: Optional[str] = None

class UpdateUserRequest(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None

class DeleteVideoRequest(BaseModel):
    video_path: str

class CreateGameContentRequest(BaseModel):
    game_id: UUID
    level: int
    content_type: str  # 'image', 'video', 'text', 'audio'
    media_path: Optional[str] = None
    question_text: str
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

class BulkDeleteGameContentRequest(BaseModel):
    content_ids: List[UUID]

# ==================== Dependency: AdminService ====================
def get_admin_service(db=Depends(get_db)) -> AdminService:
    admin_repo = AdminRepository(db)
    users_repo = UsersRepository(db)
    child_repo = ChildRepository(db)
    emotion_repo = EmotionConceptRepository(db)
    question_repo = QuestionsRepository(db)
    game_content_repo = GameContentRepo(db)
    
    return AdminService(
        admin_repo=admin_repo,
        users_repo=users_repo,
        child_repo=child_repo,
        emotion_repo=emotion_repo,
        question_repo=question_repo,
        game_content_repo=game_content_repo
    )

# ==================== User Management Endpoints ====================
@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: AdminService = Depends(get_admin_service)
):
    """Lấy danh sách tất cả users với pagination"""
    result = service.get_all_users(skip, limit)
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.post("/users")
async def create_user(
    request: CreateUserRequest,
    service: AdminService = Depends(get_admin_service)
):
    try:
        result = service.create_user(request.dict())
        
        if result["status"] != "success":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Create user error: {e}")
        raise HTTPException(500, detail=f"Lỗi tạo user: {str(e)}")

@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: UUID,
    service: AdminService = Depends(get_admin_service)
):
    """Lấy thông tin chi tiết của một user"""
    result = service.get_user_by_id(user_id)
    
    if result["status"] != "success":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result

@router.put("/users/{user_id}")
async def update_user(
    user_id: UUID,
    request: UpdateUserRequest,
    service: AdminService = Depends(get_admin_service)
):
    """Cập nhật thông tin user"""
    result = service.update_user(user_id, request.dict(exclude_unset=True))
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    service: AdminService = Depends(get_admin_service)
):
    """Xóa user"""
    result = service.delete_user(user_id)
    
    if result["status"] != "success":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result

@router.get("/children")
async def list_children(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: AdminService = Depends(get_admin_service)
):
    """Lấy danh sách tất cả children"""
    result = service.get_all_children(skip, limit)
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.get("/users/search")
async def search_users(
    name: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: AdminService = Depends(get_admin_service)
):
    """Tìm kiếm users theo tên"""
    result = service.search_users(name, skip, limit)
    
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

# ==================== GAME CONTENT MANAGEMENT ====================

@router.get("/game-contents")
async def list_game_contents(
    game_id: Optional[UUID] = Query(None),
    level: Optional[int] = Query(None),
    emotion: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: AdminService = Depends(get_admin_service)
):
    try:
        result = service.get_game_contents(
            game_id=game_id,
            level=level,
            emotion=emotion,
            skip=skip,
            limit=limit
        )
        
        if result["status"] != "success":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except Exception as e:
        print(f"❌ List game contents error: {e}")
        raise HTTPException(500, detail=f"Lỗi lấy danh sách: {str(e)}")

@router.get("/game-contents/{content_id}")
async def get_game_content_detail(
    content_id: UUID,
    service: AdminService = Depends(get_admin_service)
):
    """
    ⭐ LẤY CHI TIẾT MỘT GAME CONTENT
    """
    try:
        result = service.get_game_content_by_id(content_id)
        
        if result["status"] != "success":
            raise HTTPException(status_code=404, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Get game content error: {e}")
        raise HTTPException(500, detail=f"Lỗi lấy chi tiết: {str(e)}")

@router.post("/game-contents")
async def create_game_content(
    request: CreateGameContentRequest,
    service: AdminService = Depends(get_admin_service)
):
    """
    ⭐ TẠO MỚI GAME CONTENT
    
    Tạo nội dung câu hỏi mới cho game
    """
    try:
        result = service.create_game_content(request.dict())
        
        if result["status"] != "success":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Create game content error: {e}")
        raise HTTPException(500, detail=f"Lỗi tạo nội dung: {str(e)}")

@router.put("/game-contents/{content_id}")
async def update_game_content(
    content_id: UUID,
    request: UpdateGameContentRequest,
    service: AdminService = Depends(get_admin_service)
):
    """
    ⭐ CẬP NHẬT GAME CONTENT
    
    Cập nhật thông tin nội dung câu hỏi
    """
    try:
        result = service.update_game_content(
            content_id, 
            request.dict(exclude_unset=True)
        )
        
        if result["status"] != "success":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Update game content error: {e}")
        raise HTTPException(500, detail=f"Lỗi cập nhật: {str(e)}")

@router.delete("/game-contents/{content_id}")
async def delete_game_content(
    content_id: UUID,
    service: AdminService = Depends(get_admin_service)
):
    """
    ⭐ XÓA MỘT GAME CONTENT
    
    Xóa nội dung câu hỏi (soft delete hoặc hard delete)
    """
    try:
        result = service.delete_game_content(content_id)
        
        if result["status"] != "success":
            raise HTTPException(status_code=404, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Delete game content error: {e}")
        raise HTTPException(500, detail=f"Lỗi xóa nội dung: {str(e)}")

@router.post("/game-contents/bulk-delete")
async def bulk_delete_game_contents(
    request: BulkDeleteGameContentRequest,
    service: AdminService = Depends(get_admin_service)
):
    """
    ⭐ XÓA NHIỀU GAME CONTENTS CÙNG LÚC
    
    Xóa hàng loạt theo danh sách content_ids
    """
    try:
        result = service.bulk_delete_game_contents(request.content_ids)
        
        if result["status"] != "success":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Bulk delete error: {e}")
        raise HTTPException(500, detail=f"Lỗi xóa hàng loạt: {str(e)}")

@router.post("/game-contents/upload-media")
async def upload_game_content_media(
    file: UploadFile = File(...),
    content_type: str = Form(...),  # 'image', 'video', 'audio'
    game_name: str = Form(...),
    emotion: Optional[str] = Form(None)
):
    """
    ⭐ UPLOAD FILE MEDIA CHO GAME CONTENT
    
    - Upload ảnh/video/audio
    - Lưu vào thư mục tương ứng
    - Trả về đường dẫn file
    """
    try:
        # Validate content type
        allowed_types = {
            'image': ['image/jpeg', 'image/png', 'image/jpg', 'image/gif'],
            'video': ['video/mp4', 'video/mpeg', 'video/quicktime'],
            'audio': ['audio/mpeg', 'audio/wav', 'audio/mp3']
        }
        
        if content_type not in allowed_types:
            raise HTTPException(400, detail="Loại file không hợp lệ!")
        
        if file.content_type not in allowed_types[content_type]:
            raise HTTPException(
                400, 
                detail=f"File phải là {', '.join(allowed_types[content_type])}"
            )
        
        # Check file size (max 50MB)
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > 50 * 1024 * 1024:
            raise HTTPException(400, detail="File quá lớn! Tối đa 50MB.")
        
        # Determine save directory
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        
        if content_type == 'image':
            media_dir = project_root / "fe" / "assets" / "images" / game_name.lower()
        elif content_type == 'video':
            media_dir = project_root / "fe" / "assets" / "videos" / game_name.lower()
        else:  # audio
            media_dir = project_root / "fe" / "assets" / "audio"
        
        # Create directory if not exists
        media_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        file_ext = Path(file.filename).suffix
        if emotion:
            new_filename = f"{emotion}{file_ext}"
        else:
            new_filename = file.filename
        
        new_file_path = media_dir / new_filename
        
        # Save file
        with open(new_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Generate relative path for frontend
        relative_path = f"/fe/assets/{content_type}s/{game_name.lower()}/{new_filename}"
        
        print(f"✅ Đã lưu file: {new_file_path}")
        
        return {
            "status": "success",
            "message": "Upload thành công!",
            "data": {
                "media_path": relative_path,
                "file_size": file_size,
                "filename": new_filename
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Upload media error: {e}")
        raise HTTPException(500, detail=f"Lỗi upload file: {str(e)}")

# ==================== VIDEO MANAGEMENT (CŨ - GIỮ NGUYÊN) ====================
@router.post("/emotions/upload-video")
async def upload_emotion_video(
    video_file: UploadFile = File(...),
    emotion_id: str = Form(...),
    emotion_name: str = Form(...),
    old_path: str = Form(...)
):
    """
    ⭐ UPLOAD/THAY THẾ VIDEO DẠY CẢM XÚC
    
    - Nhận file video từ frontend
    - Lưu vào thư mục /fe/assets/videos/
    - Xóa video cũ nếu có
    - Trả về đường dẫn video mới
    """
    try:
        # Kiểm tra định dạng file
        if not video_file.content_type.startswith('video/'):
            raise HTTPException(400, detail="File không phải video!")
        
        # Kiểm tra kích thước (max 50MB)
        video_file.file.seek(0, 2)
        file_size = video_file.file.tell()
        video_file.file.seek(0)
        
        if file_size > 50 * 1024 * 1024:
            raise HTTPException(400, detail="Video quá lớn! Tối đa 50MB.")
        
        # Đường dẫn thư mục lưu video
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        video_dir = project_root / "fe" / "assets" / "videos"
        
        # Tạo thư mục nếu chưa tồn tại
        video_dir.mkdir(parents=True, exist_ok=True)
        
        # Map emotion_id sang filename chuẩn
        EMOTION_FILENAMES = {
            'vui': 'happy.mp4',
            'buon': 'sad.mp4',
            'tuc': 'angry.mp4',
            'so': 'fear.mp4',
            'ngac': 'surprise.mp4',
            'ghe': 'disgust.mp4'
        }
        
        new_filename = EMOTION_FILENAMES.get(emotion_id, f"{emotion_id}.mp4")
        new_file_path = video_dir / new_filename
        
        # XÓA VIDEO CŨ NẾU TỒN TẠI
        if new_file_path.exists():
            new_file_path.unlink()
            print(f"✅ Đã xóa video cũ: {new_file_path}")
        
        # LƯU VIDEO MỚI
        with open(new_file_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)
        
        # Đường dẫn tương đối (để frontend dùng)
        relative_path = f"../../assets/videos/{new_filename}"
        
        print(f"✅ Đã lưu video: {new_file_path}")
        
        return {
            "status": "success",
            "message": f"Đã thay thế video '{emotion_name}' thành công!",
            "data": {
                "video_path": relative_path,
                "file_size": file_size,
                "filename": new_filename
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Upload error: {e}")
        raise HTTPException(500, detail=f"Lỗi upload video: {str(e)}")

@router.post("/emotions/delete-video")
async def delete_emotion_video(request: DeleteVideoRequest):
    """
    ⭐ XÓA VIDEO DẠY CẢM XÚC
    
    - Xóa file video khỏi thư mục /fe/assets/videos/
    """
    try:
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        
        # Extract filename từ path
        # VD: "../../assets/videos/happy.mp4" → "happy.mp4"
        filename = Path(request.video_path).name
        full_path = project_root / "fe" / "assets" / "videos" / filename
        
        # Kiểm tra file có tồn tại không
        if not full_path.exists():
            raise HTTPException(404, detail="Video không tồn tại!")
        
        # XÓA FILE
        full_path.unlink()
        print(f"✅ Đã xóa video: {full_path}")
        
        return {
            "status": "success",
            "message": "Đã xóa video thành công!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Delete error: {e}")
        raise HTTPException(500, detail=f"Lỗi xóa video: {str(e)}")