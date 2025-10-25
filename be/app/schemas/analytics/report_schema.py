from uuid import UUID
from pydantic import BaseModel, Field
from typing import Dict
from datetime import datetime
from ..enum import ReportTypeEnum

class ReportSchema(BaseModel):


    class ReportRequest(BaseModel):
        child_id: UUID
        report_type: ReportTypeEnum
        summary: str = Field(..., max_length=1000)
        data: Dict = Field(...)

    class ReportResponse(BaseModel):
        report_id: UUID
        child_id: UUID
        report_type: ReportTypeEnum
        generated_at: datetime
        summary: str
        data: Dict