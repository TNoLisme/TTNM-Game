# be/app/controllers/reports_controller.py (ACCURATE TO DATABASE SCHEMA + RESEND)
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from uuid import UUID
from datetime import datetime, timedelta
from app.database import get_db
from app.repository.users_repo import UsersRepository
from app.repository.child_repo import ChildRepository
from app.repository.report_repo import ReportRepository
from app.services.analytics.report_service import ReportService
from pydantic import BaseModel
from typing import Optional
import json

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

class GenerateReportRequest(BaseModel):
    child_user_id: str
    report_type: str = "weekly"

# ==================== STATISTICS ENDPOINT ====================
@router.get("/statistics")
async def get_report_statistics(db=Depends(get_db)):
    """Debug report_type issue"""
    try:
        print("\n" + "="*60)
        print("📊 GET REPORT STATISTICS - DEBUG MODE")
        print("="*60)
        
        report_repo = ReportRepository(db)
        user_repo = UsersRepository(db)
        
        all_reports = report_repo.get_all_ordered()
        print(f"📦 Total reports in DB: {len(all_reports)}")
        
        weekly_reports = []
        monthly_reports = []
        seen_ids = set()
        
        for report in all_reports:
            report_id_str = str(report.report_id)
            
            if report_id_str in seen_ids:
                continue
            seen_ids.add(report_id_str)
            
            # 🔥 DEBUG: In ra TOÀN BỘ thông tin của report object
            print(f"\n🔍 DEBUG Report: {report_id_str[:8]}...")
            print(f"   report.report_type = {report.report_type}")
            print(f"   type(report.report_type) = {type(report.report_type)}")
            print(f"   hasattr 'value' = {hasattr(report.report_type, 'value')}")
            
            if hasattr(report.report_type, 'value'):
                print(f"   report.report_type.value = {report.report_type.value}")
            
            print(f"   dir(report.report_type) = {dir(report.report_type)}")
            print(f"   All report attributes: {dir(report)}")
            
            # Thử nhiều cách extract
            report_type_str = None
            
            # Cách 1: Enum value
            if hasattr(report.report_type, 'value'):
                report_type_str = report.report_type.value
                print(f"   ✅ Method 1 (Enum.value): {report_type_str}")
            
            # Cách 2: String conversion
            if not report_type_str:
                report_type_str = str(report.report_type)
                print(f"   ✅ Method 2 (str()): {report_type_str}")
            
            # Cách 3: Direct access nếu là string
            if not report_type_str and isinstance(report.report_type, str):
                report_type_str = report.report_type
                print(f"   ✅ Method 3 (direct): {report_type_str}")
            
            # Cách 4: Lowercase name attribute
            if not report_type_str and hasattr(report.report_type, 'name'):
                report_type_str = report.report_type.name.lower()
                print(f"   ✅ Method 4 (name.lower()): {report_type_str}")
            
            print(f"   🎯 FINAL report_type_str = {report_type_str}")
            
            # Get user
            user = user_repo.get_user_by_id(report.child_id)
            if not user:
                print(f"   ⚠️ User not found")
                continue
            
            # Parse data
            parsed_data = {}
            try:
                if isinstance(report.data, str):
                    parsed_data = json.loads(report.data)
                elif isinstance(report.data, dict):
                    parsed_data = report.data
            except:
                pass
            
            # 🔥 BUILD DICT với report_type
            report_dict = {
                "report_id": report_id_str,
                "child_id": str(report.child_id),
                "child_name": user.name,
                "child_email": user.email,
                "report_type": report_type_str,  # 🔥 CRITICAL!
                "generated_at": report.generated_at.isoformat(),
                "summary": report.summary,
                "stats": {
                    "total_sessions": parsed_data.get("total_sessions", 0),
                    "total_playtime": parsed_data.get("total_playtime", 0),
                    "avg_score": parsed_data.get("avg_score", 0)
                }
            }
            
            print(f"   📦 report_dict['report_type'] = {report_dict.get('report_type')}")
            
            # Classify
            if report_type_str == 'weekly':
                weekly_reports.append(report_dict)
                print(f"   ✅ → Added to WEEKLY")
            elif report_type_str == 'monthly':
                monthly_reports.append(report_dict)
                print(f"   ✅ → Added to MONTHLY")
            else:
                print(f"   ⚠️ → UNKNOWN TYPE!")
        
        print(f"\n📊 FINAL COUNTS:")
        print(f"   Weekly: {len(weekly_reports)}")
        print(f"   Monthly: {len(monthly_reports)}")
        
        # Print first report để verify
        if weekly_reports:
            print(f"\n🔍 Sample weekly report:")
            print(f"   {weekly_reports[0]}")
        
        # Calculate trends (giữ nguyên)
        now = datetime.now()
        last_week = now - timedelta(days=7)
        
        recent_weekly = report_repo.count_by_date_range(last_week, now, 'weekly')
        prev_weekly = report_repo.count_by_date_range(
            last_week - timedelta(days=7), 
            last_week, 
            'weekly'
        )
        weekly_trend = ((recent_weekly - prev_weekly) / prev_weekly * 100) if prev_weekly > 0 else 0
        
        last_month = now - timedelta(days=30)
        recent_monthly = report_repo.count_by_date_range(last_month, now, 'monthly')
        prev_monthly = report_repo.count_by_date_range(
            last_month - timedelta(days=30), 
            last_month, 
            'monthly'
        )
        monthly_trend = ((recent_monthly - prev_monthly) / prev_monthly * 100) if prev_monthly > 0 else 0
        
        result = {
            "weekly_reports": weekly_reports,
            "monthly_reports": monthly_reports,
            "weekly_trend": round(weekly_trend, 1),
            "monthly_trend": round(monthly_trend, 1),
            "total_count": len(seen_ids)
        }
        
        print("\n" + "="*60)
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
# ==================== ADMIN ENDPOINTS ====================

@router.post("/generate-and-send")
async def generate_and_send_report(
    request: GenerateReportRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db)
):
    """Admin tạo và gửi báo cáo cho một trẻ"""
    try:
        user_repo = UsersRepository(db)
        child_repo = ChildRepository(db)
        report_repo = ReportRepository(db)
        service = ReportService(user_repo, child_repo, report_repo)
        
        child_user_id = UUID(request.child_user_id)
        user = user_repo.get_user_by_id(child_user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy trẻ")
        
        background_tasks.add_task(
            service.generate_and_send_report,
            child_user_id,
            request.report_type
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
    report_type: str = Query("weekly", regex="^(weekly|monthly)$"),
    background_tasks: BackgroundTasks = None,
    db=Depends(get_db)
):
    """Admin gửi báo cáo hàng loạt"""
    try:
        user_repo = UsersRepository(db)
        child_repo = ChildRepository(db)
        report_repo = ReportRepository(db)
        service = ReportService(user_repo, child_repo, report_repo)
        
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
                        report_type
                    )
                else:
                    result = service.generate_and_send_report(child_user_id, report_type)
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

# ==================== USER ENDPOINTS ====================

@router.post("/request-report")
async def request_own_report(
    report_type: str = Query("weekly", regex="^(weekly|monthly)$"),
    user_id: str = Query(...), 
    background_tasks: BackgroundTasks = None,
    db=Depends(get_db)
):
    try:
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="User ID không hợp lệ")
        
        user_repo = UsersRepository(db)
        child_repo = ChildRepository(db)
        report_repo = ReportRepository(db)
        
        user = user_repo.get_user_by_id(user_uuid)
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
        
        if not user.email:
            raise HTTPException(
                status_code=400,
                detail="Tài khoản chưa có email. Vui lòng cập nhật email trong profile."
            )
        
        service = ReportService(user_repo, child_repo, report_repo)
        
        if background_tasks:
            background_tasks.add_task(
                service.generate_and_send_report,
                user_uuid,
                report_type
            )
            
            return {
                "status": "success",
                "message": f"Đang tạo báo cáo {report_type}. Email sẽ được gửi đến {user.email} trong giây lát.",
                "email": user.email,
                "will_save_to_db": True
            }
        else:
            result = service.generate_and_send_report(user_uuid, report_type)
            return result
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ==================== MANAGEMENT ENDPOINTS ====================

@router.get("/history")
async def get_report_history(
    user_id: str = Query(..., description="Child user ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db=Depends(get_db)
):
    try:
        user_uuid = UUID(user_id)
        report_repo = ReportRepository(db)
        
        reports = report_repo.get_by_child(user_uuid)
        reports.sort(key=lambda r: r.generated_at, reverse=True)
        paginated = reports[skip:skip+limit]
        
        return {
            "status": "success",
            "total": len(reports),
            "skip": skip,
            "limit": limit,
            "reports": [
                {
                    "report_id": str(r.report_id),
                    "report_type": r.report_type.value if hasattr(r.report_type, 'value') else str(r.report_type),
                    "generated_at": r.generated_at.isoformat(),
                    "summary": r.summary
                }
                for r in paginated
            ]
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="User ID không hợp lệ")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{report_id}")
async def get_report_detail(
    report_id: UUID,
    db=Depends(get_db)
):
    """Get report detail by ID"""
    try:
        report_repo = ReportRepository(db)
        user_repo = UsersRepository(db)
        
        report = report_repo.get_by_id(report_id)
        
        if not report:
            raise HTTPException(status_code=404, detail="Không tìm thấy báo cáo")
        
        # ✅ Get user info
        user = user_repo.get_user_by_id(report.child_id)
        
        # ✅ Parse data field
        parsed_data = {}
        try:
            if isinstance(report.data, str):
                parsed_data = json.loads(report.data)
            elif isinstance(report.data, dict):
                parsed_data = report.data
        except:
            pass
        
        return {
            "status": "success",
            "report_id": str(report.report_id),
            "child_id": str(report.child_id),
            "child_name": user.name if user else "N/A",
            "child_email": user.email if user else "N/A",
            "report_type": report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type),
            "generated_at": report.generated_at.isoformat(),
            "summary": report.summary,
            "data": parsed_data  # ✅ Return as dict, not string
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preview/{child_user_id}")
async def preview_report(
    child_user_id: UUID,
    report_type: str = Query("weekly", regex="^(weekly|monthly)$"),
    db=Depends(get_db)
):
    """Xem trước dữ liệu báo cáo (không lưu database)"""
    try:
        user_repo = UsersRepository(db)
        child_repo = ChildRepository(db)
        report_repo = ReportRepository(db)
        service = ReportService(user_repo, child_repo, report_repo)
        
        child_data = service._get_child_info(child_user_id)
        if not child_data:
            raise HTTPException(status_code=404, detail="Không tìm thấy trẻ")
        
        progress_data = service._get_progress_data(child_user_id, report_type)
        
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

# ==================== ADMIN MANAGEMENT ====================

@router.get("/all")
async def get_all_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    report_type: Optional[str] = Query(None, regex="^(weekly|monthly)$"),
    db=Depends(get_db)
):
    try:
        report_repo = ReportRepository(db)
        
        if report_type:
            reports = report_repo.get_by_type(report_type, skip, limit)
            total = report_repo.count_by_type(report_type)
        else:
            reports = report_repo.get_all(skip, limit)
            total = report_repo.count_all()
        
        return {
            "status": "success",
            "total": total,
            "skip": skip,
            "limit": limit,
            "reports": [
                {
                    "report_id": str(r.report_id),
                    "child_id": str(r.child_id),
                    "report_type": r.report_type.value if hasattr(r.report_type, 'value') else str(r.report_type),
                    "generated_at": r.generated_at.isoformat(),
                    "summary": r.summary
                }
                for r in reports
            ]
        }
        
    except Exception as e:
        import traceback
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
        report_repo = ReportRepository(db)
        service = ReportService(user_repo, child_repo, report_repo)
        
        result = service.send_test_email(email)
        
        if result['status'] == 'success':
            return result
        else:
            raise HTTPException(status_code=500, detail=result['message'])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))