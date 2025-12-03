
from uuid import UUID
from typing import List
from datetime import datetime
import enum
from app.domain.users.user import User
from app.domain.enum import RoleEnum
from app.domain.analytics.child_progress import ChildProgress
from app.domain.sessions.session import Session
import enum
from datetime import date
from app.domain.enum import ReportTypeEnum, GenderEnum


class Child(User):
    def __init__(self, user_id: str, age: int, last_played: date, report_preferences: ReportTypeEnum,
                 created_at: date, last_login: date, gender: GenderEnum, date_of_birth: date, phone_number: str, progress: List['ChildProgress'] = None):
        self.user_id = user_id
        self.age = age
        self.last_played = last_played
        self.report_preferences = report_preferences
        self.created_at = created_at
        self.last_login = last_login
        self.gender = gender
        self.date_of_birth = date_of_birth
        self.phone_number = phone_number
        self.progress = progress or []
