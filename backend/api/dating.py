from fastapi import APIRouter, Depends, Request, HTTPException
from dependencies import get_current_user, get_dating_service, get_session_service
from utils.responses import success_response

router = APIRouter(prefix="/dating", tags=["dating"])

@router.post("")
async def create_dating_post(
    request: Request, 
    user_id: int = Depends(get_current_user),
    dating_service = Depends(get_dating_service)
):
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
        return success_response({"post": post})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create dating post")

@router.get("")
async def get_dating_posts(request: Request, session_service = Depends(get_session_service), dating_service = Depends(get_dating_service)):
    try:
        user_id = request.cookies.get("session_id")
        if user_id:
            user_id = await session_service.get_user_id(user_id)
    except:
        user_id = None
    
    filters = dict(request.query_params)
    try:
        posts = dating_service.get_dating_posts(filters if filters else None, user_id)
        return success_response({"posts": posts})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get dating posts")

@router.post("/{post_id}/message")
async def send_message(
    post_id: int, 
    request: Request, 
    user_id: int = Depends(get_current_user),
    dating_service = Depends(get_dating_service)
):
    data = await request.json()
    try:
        message = dating_service.send_message(
            sender_id=user_id,
            dating_post_id=post_id,
            content=data.get("content")
        )
        return success_response({"message": message})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send message")

@router.get("/can_post")
async def can_post_dating(
    user_id: int = Depends(get_current_user),
    dating_service = Depends(get_dating_service)
):
    try:
        can_post = dating_service.can_post_today(user_id)
        return success_response({"can_post": can_post})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to check posting status")