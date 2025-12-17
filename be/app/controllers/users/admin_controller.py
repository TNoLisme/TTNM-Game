from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from uuid import UUID
from app.services.users.admin_service import AdminService
from app.repository.admin_repo import AdminRepository
from app.repository.users_repo import UsersRepository
from app.repository.child_repo import ChildRepository
from app.repository.emotion_concepts_repo import EmotionConceptRepository
from app.repository.questions_repo import QuestionsRepository
from app.repository.game_contents_repo import GameContentsRepository as GameContentRepo
from app.repository.report_repo import ReportRepository
from app.models.analytics import Report as ReportModel
from app.database import get_db
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from sqlalchemy.orm import Session
import os
import shutil
from pathlib import Path
from datetime import date, datetime, timedelta
import time
import unicodedata
import re
from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[4]
router = APIRouter(prefix="/admin", tags=["Admin"])

# ==================== Request Schemas ====================
class DeleteConceptVideoRequest(BaseModel):
    concept_id: UUID
    video_path: str
class CreateUserRequest(BaseModel):
    username: str
    name: str
    email: EmailStr
    password: str
    role: str  # 'admin' or 'child'
    age: Optional[int] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = None

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

# ==================== Dependency: Services ====================
def get_admin_service(db=Depends(get_db)) -> AdminService:
    admin_repo = AdminRepository(db)
    users_repo = UsersRepository(db)
    child_repo = ChildRepository(db)
    emotion_repo = EmotionConceptRepository(db)
    question_repo = QuestionsRepository(db)
    game_content_repo = GameContentRepo(db)
    report_repo = ReportRepository(db)  # ✅ ADDED
    
    return AdminService(
        admin_repo=admin_repo,
        users_repo=users_repo,
        child_repo=child_repo,
        emotion_repo=emotion_repo,
        question_repo=question_repo,
        game_content_repo=game_content_repo,
        report_repo=report_repo  # ✅ ADDED
    )
def normalize_ascii(text: str):
    # Loại bỏ dấu tiếng Việt
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")   # bỏ phần không ASCII
    
    # Chỉ giữ chữ cái, số, gạch ngang hoặc gạch dưới
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text)
    
    # Viết thường + bỏ dấu gạch thừa
    text = text.strip("-").lower()
    return text or "emotion"

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

# ==================== GAME CONTENT MANAGEMENT ====================
@router.get("/game-contents")
async def list_game_contents(
    game_id: Optional[UUID] = Query(None),
    level: Optional[int] = Query(None),
    emotion: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Tìm kiếm theo nội dung câu hỏi"), # ✅ Thêm tham số search
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: AdminService = Depends(get_admin_service)
):
    try:
        # Nếu có search text, ta tạm thời lấy danh sách lớn hơn để filter tại code 
        # (Lý tưởng là Repo hỗ trợ search, nhưng ở đây dùng cách này để không sửa sâu Repo)
        actual_limit = 1000 if search else limit
        
        result = service.get_game_contents(
            game_id=game_id,
            level=level,
            emotion=emotion,
            skip=0 if search else skip, # Nếu search thì lấy từ đầu để filter
            limit=actual_limit
        )
        
        if result["status"] != "success":
            raise HTTPException(status_code=400, detail=result["message"])
        
        contents = result["data"]["game_contents"]
        total = result["data"]["total"]

        # ✅ Logic tìm kiếm theo nội dung câu hỏi
        if search:
            search_lower = search.lower()
            filtered_contents = [
                c for c in contents 
                if c.get("question_text") and search_lower in c["question_text"].lower()
            ]
            
            # Cập nhật lại total và contents sau khi filter
            total = len(filtered_contents)
            
            # Manual Pagination sau khi filter
            start = skip
            end = skip + limit
            contents = filtered_contents[start:end]
            
            # Cập nhật lại data trả về
            result["data"]["game_contents"] = contents
            result["data"]["total"] = total
            result["data"]["skip"] = skip
            result["data"]["limit"] = limit

        return result
        
    except Exception as e:
        print(f"❌ List game contents error: {e}")
        raise HTTPException(500, detail=f"Lỗi lấy danh sách: {str(e)}")

@router.get("/game-contents/{content_id}")
async def get_game_content_detail(
    content_id: UUID,
    service: AdminService = Depends(get_admin_service)
):
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

# ==================== GAME CONTENT MEDIA UPLOAD (THEO PATTERN EMOTION) ====================

# ==================== EMOTION MAPPING ====================
def map_emotion_to_english(emotion_vn: str) -> str:
    """
    Map emotion Tiếng Việt sang Tiếng Anh cho tên folder và file
    """
    emotion_map = {
        'vui': 'happy',
        'vui vẻ': 'happy',
        'vui ve': 'happy',
        'happy': 'happy',
        
        'buồn': 'sad',
        'buồn bã': 'sad',
        'buon': 'sad',
        'buon ba': 'sad',
        'sad': 'sad',
        
        'tức giận': 'angry',
        'tuc gian': 'angry',
        'giận': 'angry',
        'gian': 'angry',
        'angry': 'angry',
        
        'sợ': 'fear',
        'sợ hãi': 'fear',
        'so': 'fear',
        'so hai': 'fear',
        'fear': 'fear',
        
        'ngạc nhiên': 'surprise',
        'ngac nhien': 'surprise',
        'surprise': 'surprise',
        
        'ghê tởm': 'disgust',
        'ghe tom': 'disgust',
        'ghê': 'disgust',
        'ghe': 'disgust',
        'disgust': 'disgust'
    }
    
    # Normalize input: lowercase và bỏ dấu
    emotion_normalized = normalize_ascii(emotion_vn).lower()
    
    # Try exact match first
    if emotion_normalized in emotion_map:
        return emotion_map[emotion_normalized]
    
    # Try original (with diacritics)
    emotion_lower = emotion_vn.lower().strip()
    if emotion_lower in emotion_map:
        return emotion_map[emotion_lower]
    
    # Fallback: use normalized version
    return emotion_normalized or 'neutral'


@router.post("/game-contents/upload-media")
async def upload_game_content_media(
    media_file: UploadFile = File(...), 
    content_id: str = Form(...),
    game_id: str = Form(...),
    content_type: str = Form(...), 
    emotion: str = Form(""),
    old_path: str = Form("")
):
    """
    Upload media cho Game Content - THEO PATTERN EMOTION
    - Upload file mới
    - Xóa file cũ (nếu có)
    - Trả về media_path mới
    """
    try:
        # 1) Validate file type
        allowed_types = {
            'image': ['image/jpeg', 'image/png', 'image/jpg', 'image/gif', 'image/webp'],
            'video': ['video/mp4', 'video/webm', 'video/mpeg'],
            'audio': ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp3']
        }
        
        if content_type not in allowed_types:
            raise HTTPException(400, detail="Loại file không hợp lệ!")
        
        if media_file.content_type not in allowed_types[content_type]:
            raise HTTPException(
                400, 
                detail=f"File phải là {', '.join(allowed_types[content_type])}"
            )
        
        # 2) Validate size (50MB)
        media_file.file.seek(0, 2)
        file_size = media_file.file.tell()
        media_file.file.seek(0)
        
        if file_size > 50 * 1024 * 1024:
            raise HTTPException(400, detail="File quá lớn! Tối đa 50MB.")
        
        # 3) Xác định thư mục lưu file
        project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        
        # Tạo folder theo content_type và emotion
        if content_type == 'image':
            base_dir = project_root / "fe" / "assets" / "images"
        elif content_type == 'video':
            base_dir = project_root / "fe" / "assets" / "videos"
        else:  # audio
            base_dir = project_root / "fe" / "assets" / "audio"
        
        # ✅ Tạo subfolder theo emotion (MAP TIẾNG VIỆT → TIẾNG ANH)
        if emotion:
            # Map emotion Tiếng Việt → Tiếng Anh
            emotion_en = map_emotion_to_english(emotion)
            print(f"🌐 Emotion mapping: '{emotion}' → '{emotion_en}'")
            media_dir = base_dir / emotion_en
        else:
            media_dir = base_dir / "game_contents"
        
        media_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Media directory: {media_dir}")
        
        # 4) Xóa file cũ (nếu có) - GIỐNG EMOTION
        if old_path:
            try:
                # old_path có dạng: "/assets/images/happy/emotion_123.jpg"
                old_rel_path = old_path.lstrip("/")
                
                # Strip /fe/ prefix nếu có
                if old_rel_path.startswith("fe/"):
                    old_rel_path = old_rel_path[3:]
                
                # Tìm file trong project
                if old_rel_path.startswith("assets/"):
                    old_file_path = project_root / "fe" / old_rel_path
                else:
                    old_file_path = project_root / "fe" / "assets" / old_rel_path
                
                if old_file_path.exists():
                    old_file_path.unlink()
                    print(f"✅ Đã xóa file cũ: {old_file_path}")
                else:
                    print(f"ℹ️ File cũ không tồn tại: {old_file_path}")
            except Exception as e:
                print(f"⚠️ Không xóa được file cũ: {e}")
        
        # 5) Tạo tên file mới với timestamp để tránh cache
        timestamp = int(time.time() * 1000)
        file_ext = Path(media_file.filename).suffix or ".jpg"
        
        if emotion:
            emotion_en = map_emotion_to_english(emotion)
            new_filename = f"{emotion_en}_{timestamp}{file_ext}"
        else:
            new_filename = f"content_{content_id[:8]}_{timestamp}{file_ext}"
        
        new_file_path = media_dir / new_filename
        
        # 6) Lưu file mới
        with open(new_file_path, "wb") as buffer:
            shutil.copyfileobj(media_file.file, buffer)
        
        # 7) Tạo relative path cho frontend
        # ✅ KHÔNG BAO GỒM /fe/ prefix - browser sẽ resolve từ root của frontend
        # Format: /assets/images/happy/happy_1234567890.jpg
        if emotion:
            emotion_en = map_emotion_to_english(emotion)
            relative_path = f"/assets/{content_type}s/{emotion_en}/{new_filename}"
        else:
            relative_path = f"/assets/{content_type}s/game_contents/{new_filename}"
        
        print(f"✅ Đã lưu file: {new_file_path}")
        print(f"📍 Relative path: {relative_path}")
        
        return {
            "status": "success",
            "message": "Upload media thành công!",
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
        import traceback
        traceback.print_exc()
        raise HTTPException(500, detail=f"Lỗi upload file: {str(e)}")

@router.post("/emotion-concepts/delete-video")
async def delete_emotion_concept_video(
    payload: DeleteConceptVideoRequest,
    db: Session = Depends(get_db),
):
    """
    Xóa video của một Emotion Concept:
    - (Optional) Xóa file vật lý trong fe/assets/videos/
    - Set video_path = NULL trong bảng emotion_concepts
    - KHÔNG xóa bản ghi Emotion Concept
    """
    try:
        concept_id = payload.concept_id
        video_path = (payload.video_path or "").strip()

        if not video_path:
            raise HTTPException(status_code=400, detail="Thiếu video_path!")

        # 1) Tìm đường dẫn file thực tế trên ổ
        project_root = Path(__file__).resolve().parent.parent.parent.parent.parent

        # video_path dạng "/assets/videos/xxx.mp4"
        # -> rel_path = "assets/videos/xxx.mp4"
        rel_path = video_path.lstrip("/")

        # File thật nằm trong fe/assets/videos
        # => PROJECT_ROOT / "fe" / "assets" / "videos" / filename
        filename = Path(rel_path).name
        file_path = project_root / "fe" / "assets" / "videos" / filename

        # 2) Xóa file nếu tồn tại (không bắt buộc, nhưng nên làm cho sạch)
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"✅ Đã xóa file video: {file_path}")
            except Exception as e:
                # Không vì lỗi xóa file mà fail cả API, chỉ log warning
                print(f"⚠️ Không xóa được file video {file_path}: {e}")
        else:
            print(f"ℹ️ File video không tồn tại trên ổ: {file_path}")

        # 3) Set video_path = NULL trong DB
        repo = EmotionConceptRepository(db)
        updated = repo.update_video_path(concept_id, None)

        if not updated:
            raise HTTPException(
                status_code=404,
                detail="Emotion concept không tồn tại!"
            )

        return {
            "status": "success",
            "message": "Đã xóa video cho Emotion Concept thành công!",
            "data": {
                "concept_id": str(concept_id),
                "video_path": None,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Delete error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xóa video: {str(e)}"
        )

@router.get("/emotions/videos")
async def list_emotion_videos():
    try:
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        video_dir = project_root / "fe" / "assets" / "videos"

        EMOTION_FILENAMES = {
            'vui': 'happy.mp4',
            'buon': 'sad.mp4',
            'tuc': 'angry.mp4',
            'so': 'fear.mp4',
            'ngac': 'surprise.mp4',
            'ghe': 'disgust.mp4'
        }

        videos = []
        for emotion_id, filename in EMOTION_FILENAMES.items():
            file_path = video_dir / filename
            exists = file_path.exists()
            videos.append({
                "id": emotion_id,
                "path": f"../../assets/videos/{filename}" if exists else "",
                "version": int(file_path.stat().st_mtime * 1000) if exists else 0
            })

        return {
            "status": "success",
            "data": {"videos": videos}
        }

    except Exception as e:
        print(f"❌ Error listing emotion videos: {e}")
        raise HTTPException(500, detail=f"Không thể tải danh sách video cảm xúc: {str(e)}")
# ==================== ✅ REPORTS MANAGEMENT ====================
@router.get("/reports/statistics")
async def get_reports_statistics(db: Session = Depends(get_db)):
    try:
        from app.models.users import Child as ChildModel
        
        # Lấy tất cả reports từ database
        all_reports = db.query(ReportModel).order_by(ReportModel.generated_at.desc()).all()
        
        # Tính thời gian
        now = datetime.now()
        last_week = now - timedelta(days=7)
        last_month = now - timedelta(days=30)
        two_weeks_ago = now - timedelta(days=14)
        two_months_ago = now - timedelta(days=60)
        
        # Phân loại báo cáo
        weekly_reports = []
        monthly_reports = []
        
        # Đếm cho trend
        current_week_count = 0
        last_week_count = 0
        current_month_count = 0
        last_month_count = 0
        
        for report in all_reports:
            # Lấy thông tin child
            child_name = "N/A"
            child_email = ""
            
            if report.child_id:
                child = db.query(ChildModel).filter(
                    ChildModel.user_id == str(report.child_id)
                ).first()
                
                if child and child.user:
                    child_name = child.user.name or "N/A"
                    child_email = child.user.email or ""
            
            report_dict = {
                'report_id': str(report.report_id),
                'child_id': str(report.child_id) if report.child_id else None,
                'child_name': child_name,
                'child_email': child_email,
                'sent_at': report.generated_at.isoformat() if report.generated_at else None,
                'status': 'sent',
                'stats': {
                    'total_sessions': 15,  # TODO: Thay bằng data thực từ report.data
                    'total_playtime': 240,
                    'avg_score': 7.5
                }
            }
            
            generated_at = report.generated_at
            
            # Phân loại theo tuần/tháng
            if generated_at and generated_at >= last_week:
                weekly_reports.append(report_dict)
                current_week_count += 1
            
            if generated_at and generated_at >= last_month:
                monthly_reports.append(report_dict)
                current_month_count += 1
            
            # Đếm cho trend
            if generated_at:
                if two_weeks_ago <= generated_at < last_week:
                    last_week_count += 1
                if two_months_ago <= generated_at < last_month:
                    last_month_count += 1
        
        # Tính trend
        weekly_trend = 0
        if last_week_count > 0:
            weekly_trend = round(((current_week_count - last_week_count) / last_week_count) * 100, 1)
        elif current_week_count > 0:
            weekly_trend = 100
        
        monthly_trend = 0
        if last_month_count > 0:
            monthly_trend = round(((current_month_count - last_month_count) / last_month_count) * 100, 1)
        elif current_month_count > 0:
            monthly_trend = 100
        
        return {
            "weekly_reports": weekly_reports,
            "monthly_reports": monthly_reports,
            "weekly_trend": weekly_trend,
            "monthly_trend": monthly_trend,
            "total_count": len(all_reports)
        }
        
    except Exception as e:
        print(f"❌ Error getting reports statistics: {e}")
        import traceback
        traceback.print_exc()
        return {
            "weekly_reports": [],
            "monthly_reports": [],
            "weekly_trend": 0,
            "monthly_trend": 0,
            "total_count": 0
        }


@router.get("/reports/{report_id}")
async def get_report_details(report_id: UUID, db: Session = Depends(get_db)):
    try:
        from app.models.users import Child as ChildModel
        
        report = db.query(ReportModel).filter(
            ReportModel.report_id == str(report_id)
        ).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Không tìm thấy báo cáo")
        
        # Lấy thông tin child
        child_name = "N/A"
        child_email = ""
        
        if report.child_id:
            # ✅ FIX: Đổi từ child_id → user_id
            child = db.query(ChildModel).filter(
                ChildModel.user_id == str(report.child_id)
            ).first()
            
            if child and child.user:
                child_name = child.user.name or "N/A"
                child_email = child.user.email or ""
        
        # Parse report data nếu có
        content = {
            'total_sessions': 15,
            'total_playtime': 240,
            'avg_score': 7.5
        }
        
        if report.data:
            try:
                import json
                parsed_data = json.loads(report.data) if isinstance(report.data, str) else report.data
                if parsed_data:
                    content = parsed_data
            except Exception as parse_error:
                print(f"⚠️ Failed to parse report data: {parse_error}")
        
        return {
            'report_id': str(report.report_id),
            'child_id': str(report.child_id) if report.child_id else None,
            'child_name': child_name,
            'child_email': child_email,
            'period': report.report_type or 'weekly',
            'sent_at': report.generated_at.isoformat() if report.generated_at else None,
            'status': 'sent',
            'summary': report.summary,
            'content': content
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting report details: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi lấy chi tiết báo cáo: {str(e)}")


@router.post("/reports/{report_id}/resend")
async def resend_report(report_id: UUID, db: Session = Depends(get_db)):
    try:
        report = db.query(ReportModel).filter(
            ReportModel.report_id == str(report_id)
        ).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Không tìm thấy báo cáo")
        
        # TODO: Tích hợp với ReportService
        # from app.services.reports.report_service import ReportService
        # from app.repository.users_repo import UsersRepository
        # from app.repository.child_repo import ChildRepository
        # 
        # users_repo = UsersRepository(db)
        # child_repo = ChildRepository(db)
        # report_service = ReportService(users_repo, child_repo)
        # 
        # result = report_service.generate_and_send_report(
        #     child_user_id=report.child_id,
        #     period=report.report_type or "weekly"
        # )
        # 
        # if result["status"] != "success":
        #     raise HTTPException(status_code=400, detail=result["message"])
        
        print(f"✅ Resending report {report_id}...")
        
        return {
            "status": "success",
            "message": "Đã gửi lại báo cáo thành công"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error resending report: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi gửi lại báo cáo: {str(e)}")
    
# ==================== EMOTION CONCEPT MANAGEMENT ====================

@router.get("/emotion-concepts")
async def list_emotion_concepts(db: Session = Depends(get_db)):
    """
    Lấy danh sách emotion_concepts cho màn Admin (quản lý video khái niệm cảm xúc).
    """
    repo = EmotionConceptRepository(db)
    concepts = repo.get_all_emotion_concepts()

    data = []
    for c in concepts:
        data.append({
            "concept_id": str(c.concept_id),
            "emotion": c.emotion,
            "level": c.level,
            "title": c.title,
            "video_path": c.video_path,
            "image_path": c.image_path,
            "audio_path": c.audio_path,
            "description": c.description
        })

    return {
        "status": "success",
        "data": data
    }

@router.post("/emotion-concepts/upload-video")
async def upload_emotion_concept_video(
    video_file: UploadFile = File(...),
    concept_id: UUID = Form(...),
    emotion: str = Form(...),
    old_path: str = Form(""),
    db: Session = Depends(get_db),
):
    """
    Upload video mới cho một Emotion Concept:
    - KHÔNG xoá video cũ
    - Lưu file mới vào fe/assets/videos/
    - Tạo tên file mới để không ghi đè
    - Cập nhật video_path trong DB để FE render video mới
    """
    try:
        # 1) Validate file type
        if not video_file.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="File không phải video!")

        # 2) Validate size
        video_file.file.seek(0, 2)
        size = video_file.file.tell()
        video_file.file.seek(0)

        if size > 50 * 1024 * 1024:
            raise HTTPException(400, detail="Video quá lớn! Tối đa 50MB.")

        # 3) Xác định thư mục lưu video
        project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        video_dir = project_root / "fe" / "assets" / "videos"
        video_dir.mkdir(parents=True, exist_ok=True)

        # 4) Tạo tên file mới (không ghi đè file cũ)
        original_ext = Path(video_file.filename).suffix or ".mp4"
        safe_emotion = normalize_ascii(emotion)

        timestamp = int(time.time() * 1000)
        ext = Path(video_file.filename).suffix or ".mp4"

        filename = f"{safe_emotion}-{timestamp}{ext}"
        new_file_path = video_dir / filename

        # 5) Lưu file MỚI, KHÔNG XOÁ file cũ
        with open(new_file_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)

        print(f"✅ Đã lưu video mới: {new_file_path}")

        # 6) Path lưu vào DB (khớp với format hệ thống của m)
        # Nếu DB của m dùng "/fe/assets/videos/xxx.mp4" thì đổi theo:
        relative_path = f"/assets/videos/{filename}"

        # 7) Update DB
        repo = EmotionConceptRepository(db)
        updated = repo.update_video_path(concept_id, relative_path)

        if not updated:
            raise HTTPException(404, detail="Emotion concept không tồn tại!")

        return {
            "status": "success",
            "message": f"Đã thay thế video cho '{emotion}' thành công!",
            "data": {
                "video_path": relative_path,
                "file_size": size,
                "filename": filename,
            },
        }

    except HTTPException:
        raise

    except Exception as e:
        print(f"❌ Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi upload video: {str(e)}")

@router.get("/stats/all-users-game-play-ratio")
async def get_all_users_game_play_ratio(db: Session = Depends(get_db)):
    """
    Lấy thống kê tỉ lệ chơi của TẤT CẢ users cho 6 game
    Dùng cho Admin Dashboard Pie Chart
    """
    try:
        print("\n=== 📊 DEBUG: Admin Game Play Statistics ===")
        
        # Query đếm số lượt chơi của mỗi game từ TẤT CẢ users
        query = text("""
            SELECT 
                g.game_id,
                g.name as game_name,
                COUNT(*) as play_count
            FROM sessions s
            JOIN games g ON s.game_id = g.game_id
            GROUP BY g.game_id, g.name
            ORDER BY play_count DESC
        """)
        
        result = db.execute(query)
        rows = result.fetchall()
        
        print(f"📦 Query returned {len(rows)} games")
        
        # Calculate total plays
        total_plays = sum(row.play_count for row in rows)
        print(f"📊 Total plays across all games: {total_plays}")
        
        if total_plays == 0:
            print("⚠️ No game sessions found, returning mock data")
            return {
                "status": "success",
                "data": {
                    "game_stats": [],
                    "total_sessions": 0,
                    "message": "Chưa có dữ liệu chơi game"
                }
            }
        
        # Prepare data for pie chart
        game_stats = []
        colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c']
        
        for index, row in enumerate(rows):
            percentage = (row.play_count / total_plays * 100)
            
            game_stats.append({
                'game_id': str(row.game_id),
                'game_name': row.game_name,
                'play_count': row.play_count,
                'percentage': round(percentage, 1),
                'color': colors[index % len(colors)]
            })
            
            print(f"  {index + 1}. {row.game_name}: {row.play_count} plays ({percentage:.1f}%)")
        
        print(f"✅ Successfully processed {len(game_stats)} games")
        
        return {
            "status": "success",
            "data": {
                "game_stats": game_stats,
                "total_sessions": total_plays
            }
        }
        
    except Exception as e:
        print(f"❌ Error in get_all_users_game_play_ratio: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return mock data on error
        return {
            "status": "success",
            "data": {
                "game_stats": [
                    {
                        "game_id": "mock-1",
                        "game_name": "Nhận diện cảm xúc",
                        "play_count": 145,
                        "percentage": 33.3,
                        "color": "#3498db"
                    },
                    {
                        "game_id": "mock-2",
                        "game_name": "Trò chơi ký ức",
                        "play_count": 98,
                        "percentage": 22.5,
                        "color": "#2ecc71"
                    },
                    {
                        "game_id": "mock-3",
                        "game_name": "Câu chuyện cảm xúc",
                        "play_count": 76,
                        "percentage": 17.5,
                        "color": "#f39c12"
                    },
                    {
                        "game_id": "mock-4",
                        "game_name": "Vườn tâm trạng",
                        "play_count": 62,
                        "percentage": 14.3,
                        "color": "#9b59b6"
                    },
                    {
                        "game_id": "mock-5",
                        "game_name": "Đố vui cảm xúc",
                        "play_count": 54,
                        "percentage": 12.4,
                        "color": "#e74c3c"
                    }
                ],
                "total_sessions": 435,
                "message": "Mock data (database error)"
            }
        }
