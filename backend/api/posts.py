from fastapi import APIRouter, Depends, Request, HTTPException
from dependencies import get_current_user, get_post_service, get_session_service
from utils.responses import success_response

router = APIRouter(prefix="/comment_posts", tags=["comment_posts"])

@router.post("")
async def create_comment_post(
    request: Request, 
    user_id: int = Depends(get_current_user),
    post_service = Depends(get_post_service)
):
    data = await request.json()
    try:
        post = post_service.create_post(
            user_id=user_id,
            target_gender=data.get("target_gender"),
            target_job=data.get("target_job"),
            target_birth_year=data.get("target_birth_year"),
            target_height=data.get("target_height"),
            target_app=data.get("target_app"),
            comment=data.get("comment")
        )
        return success_response({"post": post})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create comment post")

@router.get("")
async def get_comment_posts(request: Request, session_service = Depends(get_session_service), post_service = Depends(get_post_service)):
    try:
        user_id = request.cookies.get("session_id")
        if user_id:
            user_id = await session_service.get_user_id(user_id)
    except:
        user_id = None
    
    filters = dict(request.query_params)
    try:
        posts = post_service.get_posts(filters if filters else None, user_id)
        return success_response({"posts": posts})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get comment posts")

@router.put("/{post_id}")
async def update_comment_post(
    post_id: int, 
    request: Request, 
    user_id: int = Depends(get_current_user),
    post_service = Depends(get_post_service)
):
    data = await request.json()
    try:
        post = post_service.update_post(
            post_id=post_id,
            user_id=user_id,
            target_gender=data.get("target_gender"),
            target_job=data.get("target_job"),
            target_birth_year=data.get("target_birth_year"),
            target_height=data.get("target_height"),
            target_app=data.get("target_app"),
            comment=data.get("comment")
        )
        if not post:
            raise HTTPException(status_code=404, detail="Comment post not found or not authorized")
        return success_response({"post": post})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update comment post")

@router.post("/{post_id}/like")
async def like_comment_post(
    post_id: int, 
    user_id: int = Depends(get_current_user),
    post_service = Depends(get_post_service)
):
    try:
        success = post_service.like_post(post_id, user_id)
        return success_response({"liked": success})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to like comment post")

@router.delete("/{post_id}/like")
async def unlike_comment_post(
    post_id: int, 
    user_id: int = Depends(get_current_user),
    post_service = Depends(get_post_service)
):
    try:
        success = post_service.unlike_post(post_id, user_id)
        return success_response({"unliked": success})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to unlike comment post")