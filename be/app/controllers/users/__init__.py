
from .users_controller import router as user_router
from .admin_controller import router as admin_router

__all__ = ['admin_router', 'user_router']
