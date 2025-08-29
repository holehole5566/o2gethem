from fastapi import APIRouter, Depends, Request, HTTPException
from services.dating_service import DatingService
from dependencies import get_current_user
from config import settings

router = APIRouter(prefix="/messages", tags=["messages"])

# Initialize services
dating_service = DatingService(settings.database_dsn)

@router.get("")
async def get_messages(user_id: int = Depends(get_current_user)):
    try:
        messages = dating_service.get_messages(user_id)
        return {"status": "ok", "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get messages")

@router.post("/{message_id}/reply")
async def reply_message(message_id: int, request: Request, user_id: int = Depends(get_current_user)):
    data = await request.json()
    try:
        message = dating_service.reply_message(
            message_id=message_id,
            user_id=user_id,
            reply_content=data.get("reply_content")
        )
        return {"status": "ok", "message": message}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to reply message")

@router.put("/{message_id}")
async def update_message(message_id: int, request: Request, user_id: int = Depends(get_current_user)):
    data = await request.json()
    try:
        message = dating_service.update_message(
            message_id=message_id,
            user_id=user_id,
            content=data.get("content")
        )
        return {"status": "ok", "message": message}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update message")