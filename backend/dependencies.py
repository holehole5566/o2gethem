from fastapi import HTTPException, Request
from services.session_service import SessionService
from services.user_service import UserService
from services.post_service import PostService
from services.dating_service import DatingService
from config import settings

# Initialize services once
session_service = SessionService(redis_url=settings.redis_url, expire_minutes=settings.session_expire_minutes)
user_service = UserService(settings.database_dsn)
post_service = PostService(settings.database_dsn)
dating_service = DatingService(settings.database_dsn)

async def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        user_id = await session_service.get_user_id(session_id)
        if not user_id:
            raise HTTPException(status_code=401, detail="Session expired or invalid")
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed")

# Service dependencies
def get_user_service():
    return user_service

def get_post_service():
    return post_service

def get_dating_service():
    return dating_service

def get_session_service():
    return session_service