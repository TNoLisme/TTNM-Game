from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from uuid import UUID
from app.domain.enum import RoleEnum
from app.repository.users_repo import UsersRepository
from app.database import get_db
from sqlalchemy.orm import Session

security = HTTPBearer()

# Simple token storage (in production, use JWT or Redis)
active_sessions = {}  # Format: {token: {user_id: UUID, role: RoleEnum}}

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Lấy thông tin user hiện tại từ token"""
    token = credentials.credentials
    
    # DEBUG: Log để trace issue
    print(f"🔑 Received token: {token[:20] if len(token) > 20 else token}...")
    print(f"📊 Active sessions: {len(active_sessions)}")
    
    # Kiểm tra token trong active_sessions
    session_data = active_sessions.get(token)
    if not session_data:
        print(f"❌ Token not found in active_sessions")
        print(f"💡 Hint: Server may have restarted. Please login again.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please login again."
        )
    
    print(f"✅ Token valid for user_id: {session_data['user_id']}")
    
    # Lấy user từ database
    user_repo = UsersRepository(db)
    user = user_repo.get_user_by_id(session_data['user_id'])
    
    if not user:
        print(f"❌ User not found in database: {session_data['user_id']}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    print(f"✅ User authenticated: {user.username} (role: {user.role})")
    return user

async def require_admin(current_user = Depends(get_current_user)):
    """Middleware kiểm tra quyền admin"""
    print(f"🔒 Checking admin privileges for user: {current_user.username}")
    print(f"   Role: {current_user.role} (type: {type(current_user.role)})")
    
    if current_user.role != RoleEnum.admin:
        print(f"❌ Access denied: Not an admin")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Admin privileges required. Current role: {current_user.role}"
        )
    
    print(f"✅ Admin access granted")
    return current_user

def create_session_token(user_id: UUID, role: RoleEnum) -> str:
    """Tạo session token đơn giản (trong production nên dùng JWT)"""
    import secrets
    token = secrets.token_urlsafe(32)
    active_sessions[token] = {
        'user_id': user_id,
        'role': role
    }
    print(f"✅ Created session token for user_id: {user_id} (role: {role})")
    print(f"📊 Total active sessions: {len(active_sessions)}")
    return token

def invalidate_session_token(token: str):
    """Xóa session token (logout)"""
    if token in active_sessions:
        user_data = active_sessions[token]
        del active_sessions[token]
        print(f"✅ Invalidated session for user_id: {user_data['user_id']}")
        print(f"📊 Remaining sessions: {len(active_sessions)}")
    else:
        print(f"⚠️  Token not found for invalidation")