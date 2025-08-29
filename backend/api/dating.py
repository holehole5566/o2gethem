from fastapi import APIRouter, Depends, Request, HTTPException
from services.dating_service import DatingService
from services.session_service import SessionService
from dependencies import get_current_user
from config import settings

router = APIRouter(prefix="/dating", tags=["dating"])

# Initialize services
dating_service = DatingService(settings.database_dsn)
session_service = SessionService(redis_url=settings.redis_url, expire_minutes=settings.session_expire_minutes)

@router.post("")
async def create_dating_post(request: Request, user_id: int = Depends(get_current_user)):
    data = await request.json()
    try:
        post = dating_service.create_dating_post(
            user_id=user_id,
            title=data.get("title"),
            description=data.get("description"),
            target_gender=data.get("target_gender"),
            target_age_min=data.get("target_age_min"),
            target_age_max=data.get("target_age_max")
        )
        return {"status": "ok", "post": post}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create dating post")

@router.get("")
async def get_dating_posts(request: Request):
    try:
        user_id = request.cookies.get("session_id")
        if user_id:
            user_id = await session_service.get_user_id(user_id)
    except:
        user_id = None
    
    filters = dict(request.query_params)
    try:
        posts = dating_service.get_dating_posts(filters if filters else None, user_id)
        return {"status": "ok", "posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get dating posts")

@router.post("/{post_id}/message")
async def send_message(post_id: int, request: Request, user_id: int = Depends(get_current_user)):
    data = await request.json()
    try:
        message = dating_service.send_message(
            sender_id=user_id,
            dating_post_id=post_id,
            content=data.get("content")
        )
        return {"status": "ok", "message": message}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send message")

@router.get("/can_post")
async def can_post_dating(user_id: int = Depends(get_current_user)):
    try:
        can_post = dating_service.can_post_today(user_id)
        return {"status": "ok", "can_post": can_post}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to check posting status")