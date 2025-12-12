from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from uuid import UUID
from app.database import get_db
from app.repository.users_repo import UsersRepository
from app.repository.child_repo import ChildRepository
from app.services.analytics.report_service import ReportService
from pydantic import BaseModel
from typing import Optional
from app.current_user import get_current_user

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

class GenerateReportRequest(BaseModel):
    child_user_id: str
    period: str = "weekly"

# ==================== ADMIN ENDPOINTS ====================

@router.post("/generate-and-send")
async def generate_and_send_report(
    request: GenerateReportRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db)
):
    try:
        user_repo = UsersRepository(db)
        child_repo = ChildRepository(db)
        service = ReportService(user_repo, child_repo)
        
        child_user_id = UUID(request.child_user_id)
        user = user_repo.get_user_by_id(child_user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy trẻ")
        
        background_tasks.add_task(
            service.generate_and_send_report,
            child_user_id,
            request.period
        )
        
        return {
            "status": "success",
            "message": "Đang tạo và gửi báo cáo. Email sẽ được gửi trong giây lát."
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="ID không hợp lệ")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-batch")
async def send_batch_reports(
    child_ids: list[str],
    period: str = Query("weekly", regex="^(weekly|monthly)$"),
    background_tasks: BackgroundTasks = None,
    db=Depends(get_db)
):
    """Admin gửi báo cáo hàng loạt cho nhiều trẻ"""
    try:
        user_repo = UsersRepository(db)
        child_repo = ChildRepository(db)
        service = ReportService(user_repo, child_repo)
        
        success_count = 0
        failed = []
        
        for child_id in child_ids:
            try:
                child_user_id = UUID(child_id)
                user = user_repo.get_user_by_id(child_user_id)
                
                if not user:
                    failed.append({"id": child_id, "reason": "Không tìm thấy"})
                    continue
                
                if background_tasks:
                    background_tasks.add_task(
                        service.generate_and_send_report,
                        child_user_id,
                        period
                    )
                else:
                    result = service.generate_and_send_report(child_user_id, period)
                    if result['status'] != 'success':
                        failed.append({"id": child_id, "reason": result['message']})
                        continue
                
                success_count += 1
                
            except Exception as e:
                failed.append({"id": child_id, "reason": str(e)})
        
        return {
            "status": "success",
            "message": f"Đã gửi {success_count}/{len(child_ids)} báo cáo",
            "success_count": success_count,
            "failed": failed
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preview/{child_user_id}")
async def preview_report(
    child_user_id: UUID,
    period: str = Query("weekly", regex="^(weekly|monthly)$"),
    db=Depends(get_db)
):
    """Xem trước dữ liệu báo cáo"""
    try:
        user_repo = UsersRepository(db)
        child_repo = ChildRepository(db)
        service = ReportService(user_repo, child_repo)
        
        child_data = service._get_child_info(child_user_id)
        if not child_data:
            raise HTTPException(status_code=404, detail="Không tìm thấy trẻ")
        
        progress_data = service._get_progress_data(child_user_id, period)
        
        return {
            "status": "success",
            "child": child_data,
            "progress": progress_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ==================== USER ENDPOINTS ====================
@router.post("/request-report")
async def request_own_report(
    period: str = Query("weekly", regex="^(weekly|monthly)$"),
    user_id: str = Query(...), 
    background_tasks: BackgroundTasks = None,
    db=Depends(get_db)
):
    print(f"\n{'='*60}")
    print(f"📧 REQUEST REPORT ENDPOINT HIT")
    print(f"   User ID (from query): {user_id}")
    print(f"   Period: {period}")
    print(f"{'='*60}\n")
    
    try:
        # Chuyển string sang UUID
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="User ID không hợp lệ")
        
        user_repo = UsersRepository(db)
        child_repo = ChildRepository(db)
        
        # Lấy thông tin user
        user = user_repo.get_user_by_id(user_uuid)
        if not user:
            print(f"❌ User not found: {user_id}")
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
        
        if not user.email:
            print(f"❌ User has no email!")
            raise HTTPException(
                status_code=400,
                detail="Tài khoản chưa có email. Vui lòng cập nhật email trong profile."
            )
        
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        
        service = ReportService(user_repo, child_repo)
        
        if background_tasks:
            print(f"✅ Adding report generation to background tasks")
            background_tasks.add_task(
                service.generate_and_send_report,
                user_uuid,
                period
            )
            
            return {
                "status": "success",
                "message": f"Đang tạo báo cáo {period}. Email sẽ được gửi đến {user.email} trong giây lát.",
                "email": user.email
            }
        else:
            print(f"⚠️  No background tasks, running synchronously")
            result = service.generate_and_send_report(user_uuid, period)
            return result
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"❌ ERROR in request_own_report:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
# ==================== TEST ENDPOINT ====================

@router.post("/test-email")
async def test_email_config(
    email: str,
    db=Depends(get_db)
):
    """Test cấu hình email"""
    try:
        user_repo = UsersRepository(db)
        child_repo = ChildRepository(db)
        service = ReportService(user_repo, child_repo)
        
        result = service.send_test_email(email)
        
        if result['status'] == 'success':
            return result
        else:
            raise HTTPException(status_code=500, detail=result['message'])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
