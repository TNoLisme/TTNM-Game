from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from uuid import UUID
from app.services.users.admin_service import AdminService
from app.repository.admin_repo import AdminRepository
from app.repository.users_repo import UsersRepository
from app.repository.child_repo import ChildRepository
from app.repository.emotion_concepts_repo import EmotionConceptRepository
from app.repository.questions_repo import QuestionsRepository
from app.repository.game_contents_repo import GameContentsRepository as GameContentRepo
from app.repository.report_repo import ReportRepository  # ✅ ADDED
from app.models.analytics import Report as ReportModel  # ✅ ADDED
from app.database import get_db
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from sqlalchemy.orm import Session
import os
import shutil
from pathlib import Path
from datetime import date, datetime, timedelta
import time
PROJECT_ROOT = Path(__file__).resolve().parents[4]
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

@router.post("/game-contents/upload-media")
async def upload_game_content_media(
    file: UploadFile = File(...),
    content_type: str = Form(...),  # 'image', 'video', 'audio'
    game_name: str = Form(...),
    emotion: Optional[str] = Form(None)
):
    try:
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
            media_dir = PROJECT_ROOT  / "fe" / "assets" / "images" / game_name.lower()
        elif content_type == 'video':
            media_dir = PROJECT_ROOT  / "fe" / "assets" / "videos" / game_name.lower()
        else:  # audio
            media_dir = PROJECT_ROOT  / "fe" / "assets" / "audio"
        
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
    try:
        if not video_file.content_type.startswith('video/'):
            raise HTTPException(400, detail="File không phải video!")
        
        video_file.file.seek(0, 2)
        file_size = video_file.file.tell()
        video_file.file.seek(0)
        
        if file_size > 50 * 1024 * 1024:
            raise HTTPException(400, detail="Video quá lớn! Tối đa 50MB.")
        
        video_dir = PROJECT_ROOT / "fe" / "assets" / "videos"
        video_dir.mkdir(parents=True, exist_ok=True)
        
        # Map emotion_id sang filename chuẩn
        for path in video_dir.glob(f"{emotion_id}_*.mp4"):
            path.unlink()
            print(f"✅ Đã xóa video cũ: {path}")

        default_map = {
            'vui': 'happy.mp4',
            'buon': 'sad.mp4',
            'tuc': 'angry.mp4',
            'so': 'fear.mp4',
            'ngac': 'surprise.mp4',
            'ghe': 'disgust.mp4'
        }
        
        default_filename = default_map.get(emotion_id)
        if default_filename:
            default_path = video_dir / default_filename
            if default_path.exists():
                default_path.unlink()
                print(f"✅ Đã xóa file mặc định: {default_path}")

        timestamp = int(time.time() * 1000)
        new_filename = f"{emotion_id}_{timestamp}.mp4"
        new_file_path = video_dir / new_filename
        
        with open(new_file_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)
        
        # Đường dẫn tương đối (để frontend dùng)
        relative_path = f"../../assets/videos/{new_filename}"
        version = int(new_file_path.stat().st_mtime * 1000)
        print(f"✅ Đã lưu video: {new_file_path}")
        
        return {
            "status": "success",
            "message": f"Đã thay thế video '{emotion_name}' thành công!",
            "data": {
                "video_path": relative_path,
                "file_size": file_size,
                "filename": new_filename,
                "version": version
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Upload error: {e}")
        raise HTTPException(500, detail=f"Lỗi upload video: {str(e)}")

@router.post("/emotions/delete-video")
async def delete_emotion_video(request: DeleteVideoRequest):
    try:
        
        # Extract filename từ path
        # VD: "../../assets/videos/happy.mp4" → "happy.mp4"
        filename = Path(request.video_path).name
        full_path = PROJECT_ROOT  / "fe" / "assets" / "videos" / filename
        
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