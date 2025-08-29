from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_current_user, get_user_service, get_post_service, get_dating_service
from utils.responses import success_response

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/profile")
async def profile(
    user_id: int = Depends(get_current_user),
    user_service = Depends(get_user_service),
    post_service = Depends(get_post_service),
    dating_service = Depends(get_dating_service)
):
    try:
        user = user_service.get_user_by_id(user_id)
        user_posts = post_service.get_user_posts(user_id)
        user_dating_posts = dating_service.get_user_dating_posts(user_id)
        return success_response({
            "user_id": user_id, 
            "user": user,
            "comment_posts": user_posts,
            "dating_posts": user_dating_posts
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get profile")