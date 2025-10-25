from sqlalchemy import Column, UUID, ForeignKey
from ..base import Base

class Admin(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), primary_key=True)