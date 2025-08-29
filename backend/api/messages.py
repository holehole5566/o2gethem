from fastapi import APIRouter, Depends, Request, HTTPException
from dependencies import get_current_user, get_dating_service
from utils.responses import success_response

router = APIRouter(prefix="/messages", tags=["messages"])

@router.get("")
async def get_messages(
    user_id: int = Depends(get_current_user),
    dating_service = Depends(get_dating_service)
):
    try:
        messages = dating_service.get_messages(user_id)
        return success_response({"messages": messages})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get messages")

@router.post("/{message_id}/reply")
async def reply_message(
    message_id: int, 
    request: Request, 
    user_id: int = Depends(get_current_user),
    dating_service = Depends(get_dating_service)
):
    data = await request.json()
    try:
        message = dating_service.reply_message(
            message_id=message_id,
            user_id=user_id,
            reply_content=data.get("reply_content")
        )
        return success_response({"message": message})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to reply message")

@router.put("/{message_id}")
async def update_message(
    message_id: int, 
    request: Request, 
    user_id: int = Depends(get_current_user),
    dating_service = Depends(get_dating_service)
):
    data = await request.json()
    try:
        message = dating_service.update_message(
            message_id=message_id,
            user_id=user_id,
            content=data.get("content")
        )
        return success_response({"message": message})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update message")