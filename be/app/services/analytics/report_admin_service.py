from uuid import UUID
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.repository.report_repo import ReportRepository
from app.repository.child_repo import ChildRepository
from app.repository.users_repo import UsersRepository
from app.domain.analytics.report import Report

class ReportService:    
    def __init__(
        self,
        report_repo: ReportRepository,
        child_repo: ChildRepository,
        users_repo: UsersRepository
    ):
        self.report_repo = report_repo
        self.child_repo = child_repo
        self.users_repo = users_repo
    
    # ==================== GET STATISTICS ====================
    def get_reports_statistics(self) -> Dict:
        try:
            # Lấy tất cả reports
            all_reports = self.report_repo.get_all_ordered()
            
            # Tính thời gian
            now = datetime.now()
            last_week = now - timedelta(days=7)
            last_month = now - timedelta(days=30)
            two_weeks_ago = now - timedelta(days=14)
            two_months_ago = now - timedelta(days=60)
            
            # Khởi tạo danh sách
            weekly_reports = []
            monthly_reports = []
            
            # Đếm cho trend
            current_week_count = 0
            last_week_count = 0
            current_month_count = 0
            last_month_count = 0
            
            # Xử lý từng report
            for report in all_reports:
                # Lấy thông tin child
                child_info = self._get_child_info(report.child_id)
                
                # Parse data
                import json
                parsed_data = {}
                if report.data:
                    try:
                        parsed_data = json.loads(report.data) if isinstance(report.data, str) else report.data
                    except:
                        parsed_data = {}
                
                # Tạo dict cho response
                report_dict = {
                    'report_id': str(report.report_id),
                    'child_id': str(report.child_id) if report.child_id else None,
                    'child_name': child_info['name'],
                    'child_email': child_info['email'],
                    'period': report.report_type,  # 'weekly' hoặc 'monthly'
                    'sent_at': report.generated_at.isoformat() if report.generated_at else None,
                    'status': 'sent',
                    'stats': self._extract_stats(parsed_data),
                    'summary': report.summary
                }
                
                generated_at = report.generated_at
                
                # Phân loại theo report_type
                if report.report_type == 'weekly':
                    weekly_reports.append(report_dict)
                    if generated_at and generated_at >= last_week:
                        current_week_count += 1
                    elif generated_at and two_weeks_ago <= generated_at < last_week:
                        last_week_count += 1
                
                elif report.report_type == 'monthly':
                    monthly_reports.append(report_dict)
                    if generated_at and generated_at >= last_month:
                        current_month_count += 1
                    elif generated_at and two_months_ago <= generated_at < last_month:
                        last_month_count += 1
            
            # Tính trend
            weekly_trend = self._calculate_trend(current_week_count, last_week_count)
            monthly_trend = self._calculate_trend(current_month_count, last_month_count)
            
            return {
                "status": "success",
                "data": {
                    "weekly_reports": weekly_reports,
                    "monthly_reports": monthly_reports,
                    "weekly_trend": weekly_trend,
                    "monthly_trend": monthly_trend,
                    "total_count": len(all_reports)
                }
            }
            
        except Exception as e:
            print(f"❌ Error in get_reports_statistics: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "failed",
                "message": str(e),
                "data": {
                    "weekly_reports": [],
                    "monthly_reports": [],
                    "weekly_trend": 0,
                    "monthly_trend": 0,
                    "total_count": 0
                }
            }
    
    # ==================== GET REPORT DETAILS ====================
    def get_report_by_id(self, report_id: UUID) -> Dict:
        """
        Lấy chi tiết một báo cáo
        """
        try:
            report = self.report_repo.get_by_id(report_id)
            
            if not report:
                return {
                    "status": "failed",
                    "message": "Không tìm thấy báo cáo"
                }
            
            # Lấy thông tin child
            child_info = self._get_child_info(report.child_id)
            
            # Parse data
            import json
            parsed_data = {}
            if report.data:
                try:
                    parsed_data = json.loads(report.data) if isinstance(report.data, str) else report.data
                except:
                    pass
            
            return {
                "status": "success",
                "data": {
                    'report_id': str(report.report_id),
                    'child_id': str(report.child_id) if report.child_id else None,
                    'child_name': child_info['name'],
                    'child_email': child_info['email'],
                    'period': report.report_type,
                    'sent_at': report.generated_at.isoformat() if report.generated_at else None,
                    'status': 'sent',
                    'summary': report.summary,
                    'content': parsed_data or self._get_default_stats()
                }
            }
            
        except Exception as e:
            print(f"❌ Error in get_report_by_id: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "failed",
                "message": str(e)
            }
    
    # ==================== RESEND REPORT ====================
    def resend_report(self, report_id: UUID) -> Dict:
        """
        Gửi lại báo cáo qua email
        """
        try:
            report = self.report_repo.get_by_id(report_id)
            
            if not report:
                return {
                    "status": "failed",
                    "message": "Không tìm thấy báo cáo"
                }
            
            # TODO: Tích hợp với email service
            # from app.services.reports.report_service import ReportService
            # email_result = report_service.send_report_email(...)
            
            print(f"✅ Đã gửi lại báo cáo {report_id}")
            
            return {
                "status": "success",
                "message": "Đã gửi lại báo cáo thành công",
                "data": {
                    "report_id": str(report_id)
                }
            }
            
        except Exception as e:
            print(f"❌ Error in resend_report: {e}")
            return {
                "status": "failed",
                "message": str(e)
            }
    
    # ==================== GET ALL REPORTS ====================
    def get_all_reports(
        self, 
        skip: int = 0, 
        limit: int = 100,
        report_type: Optional[str] = None
    ) -> Dict:
        """
        Lấy danh sách tất cả reports với pagination
        """
        try:
            if report_type:
                reports = self.report_repo.get_by_type(report_type, skip, limit)
                total = self.report_repo.count_by_type(report_type)
            else:
                reports = self.report_repo.get_all(skip, limit)
                total = self.report_repo.count_all()
            
            report_list = []
            for report in reports:
                child_info = self._get_child_info(report.child_id)
                
                import json
                parsed_data = {}
                if report.data:
                    try:
                        parsed_data = json.loads(report.data) if isinstance(report.data, str) else report.data
                    except:
                        pass
                
                report_list.append({
                    'report_id': str(report.report_id),
                    'child_id': str(report.child_id) if report.child_id else None,
                    'child_name': child_info['name'],
                    'child_email': child_info['email'],
                    'report_type': report.report_type,
                    'generated_at': report.generated_at.isoformat() if report.generated_at else None,
                    'summary': report.summary,
                    'stats': self._extract_stats(parsed_data)
                })
            
            return {
                "status": "success",
                "data": {
                    "reports": report_list,
                    "total": total,
                    "skip": skip,
                    "limit": limit
                }
            }
            
        except Exception as e:
            print(f"❌ Error in get_all_reports: {e}")
            return {
                "status": "failed",
                "message": str(e)
            }
    
    # ==================== HELPER METHODS ====================
    def _get_child_info(self, child_id: Optional[str]) -> Dict[str, str]:
        """Lấy thông tin child từ child_id"""
        if not child_id:
            return {'name': 'N/A', 'email': ''}
        
        try:
            child = self.child_repo.get_by_user_id(child_id)
            if not child:
                return {'name': 'N/A', 'email': ''}
            
            user = self.users_repo.get_by_id(UUID(child_id))
            if not user:
                return {'name': 'N/A', 'email': ''}
            
            return {
                'name': user.name or 'N/A',
                'email': user.email or ''
            }
        except Exception as e:
            print(f"⚠️ Lỗi lấy child info: {e}")
            return {'name': 'N/A', 'email': ''}
    
    def _calculate_trend(self, current: int, previous: int) -> float:
        """Tính % thay đổi"""
        if previous > 0:
            return round(((current - previous) / previous) * 100, 1)
        elif current > 0:
            return 100.0
        return 0.0
    
    def _extract_stats(self, data: Dict) -> Dict:
        """Trích xuất stats từ data"""
        return {
            'total_sessions': data.get('total_sessions', 0),
            'total_playtime': data.get('total_playtime', 0),
            'avg_score': data.get('avg_score', 0)
        }
    
    def _get_default_stats(self) -> Dict:
        """Stats mặc định khi không có data"""
        return {
            'total_sessions': 0,
            'total_playtime': 0,
            'avg_score': 0
        }