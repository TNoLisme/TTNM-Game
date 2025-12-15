from uuid import UUID
from sqlalchemy.orm import Session
from app.models.analytics import Report as ReportModel
from app.mapper.report_mapper import ReportMapper
from app.domain.analytics.report import Report
from .base_repo import BaseRepository
from typing import List, Optional
from datetime import datetime, timedelta

class ReportRepository(BaseRepository[ReportModel, Report]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, ReportModel, ReportMapper)

    def get_by_child(self, child_id: UUID) -> List[Report]:
        """Lấy tất cả reports của một child"""
        report_models = self.db_session.query(self.model_class).filter(
            self.model_class.child_id == child_id
        ).all()
        return [self.mapper_class.to_domain(model) for model in report_models]
    
    def get_by_id(self, report_id: UUID) -> Optional[Report]:
        """Lấy report theo report_id"""
        model = self.db_session.query(self.model_class).filter(
            self.model_class.report_id == str(report_id)
        ).first()
        
        if not model:
            return None
        
        return self.mapper_class.to_domain(model)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Report]:
        """Lấy tất cả reports với pagination"""
        report_models = self.db_session.query(self.model_class)\
            .order_by(self.model_class.generated_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        return [self.mapper_class.to_domain(model) for model in report_models]
    
    def get_all_ordered(self) -> List[Report]:
        """Lấy tất cả reports sắp xếp theo ngày tạo (mới nhất trước)"""
        report_models = self.db_session.query(self.model_class)\
            .order_by(self.model_class.generated_at.desc())\
            .all()
        return [self.mapper_class.to_domain(model) for model in report_models]
    
    def get_by_type(self, report_type: str, skip: int = 0, limit: int = 100) -> List[Report]:
        """Lấy reports theo loại (weekly/monthly)"""
        report_models = self.db_session.query(self.model_class).filter(
            self.model_class.report_type == report_type
        ).order_by(
            self.model_class.generated_at.desc()
        ).offset(skip).limit(limit).all()
        
        return [self.mapper_class.to_domain(model) for model in report_models]
    
    def get_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime,
        report_type: Optional[str] = None
    ) -> List[Report]:
        """Lấy reports trong khoảng thời gian"""
        query = self.db_session.query(self.model_class).filter(
            self.model_class.generated_at >= start_date,
            self.model_class.generated_at <= end_date
        )
        
        if report_type:
            query = query.filter(self.model_class.report_type == report_type)
        
        report_models = query.order_by(
            self.model_class.generated_at.desc()
        ).all()
        
        return [self.mapper_class.to_domain(model) for model in report_models]
    
    def count_all(self) -> int:
        """Đếm tổng số reports"""
        return self.db_session.query(self.model_class).count()
    
    def count_by_type(self, report_type: str) -> int:
        """Đếm số reports theo loại"""
        return self.db_session.query(self.model_class).filter(
            self.model_class.report_type == report_type
        ).count()
    
    def count_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime,
        report_type: Optional[str] = None
    ) -> int:
        """Đếm số reports trong khoảng thời gian"""
        query = self.db_session.query(self.model_class).filter(
            self.model_class.generated_at >= start_date,
            self.model_class.generated_at <= end_date
        )
        
        if report_type:
            query = query.filter(self.model_class.report_type == report_type)
        
        return query.count()
    
    def save(self, domain_entity: Report) -> Report:
        """Lưu/cập nhật report"""
        model = self.db_session.query(self.model_class).filter(
            self.model_class.report_id == str(domain_entity.report_id)
        ).first()
        
        if model:
            # Update existing
            model.child_id = domain_entity.child_id
            model.report_type = domain_entity.report_type
            model.generated_at = domain_entity.generated_at
            model.summary = domain_entity.summary
            model.data = domain_entity.data
        else:
            # Create new
            model = self.mapper_class.to_model(domain_entity)
            self.db_session.add(model)
        
        self.db_session.commit()
        self.db_session.refresh(model)
        
        return self.mapper_class.to_domain(model)
    
    def delete(self, report_id: UUID) -> bool:
        """Xóa report"""
        try:
            result = self.db_session.query(self.model_class).filter(
                self.model_class.report_id == str(report_id)
            ).delete()
            self.db_session.commit()
            return result > 0
        except Exception as e:
            self.db_session.rollback()
            print(f"❌ Error deleting report: {e}")
            return False