from uuid import UUID
from sqlalchemy.orm import Session
from models.users import Admin as AdminModel
from mapper.admin_mapper import AdminMapper
from domain.users.admin import Admin
from .base_repo import BaseRepository

class AdminRepository(BaseRepository[AdminModel, Admin]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, AdminModel, AdminMapper)