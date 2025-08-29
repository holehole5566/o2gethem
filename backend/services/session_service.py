import uuid
import redis.asyncio as redis
from datetime import timedelta

class SessionService:
    def __init__(self, redis_url: str = "redis://redis:6379", expire_minutes: int = 30):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.expire_seconds = expire_minutes * 60

    async def create_session(self, user_id: int) -> str:
        session_id = str(uuid.uuid4())
        await self.redis.setex(f"session:{session_id}", self.expire_seconds, user_id)
        return session_id

    async def get_user_id(self, session_id: str) -> int | None:
        user_id = await self.redis.get(f"session:{session_id}")
        if user_id:
            # 選擇性刷新 session 過期時間（滑動過期）
            await self.redis.expire(f"session:{session_id}", self.expire_seconds)
            return int(user_id)
        return None

    async def delete_session(self, session_id: str):
        await self.redis.delete(f"session:{session_id}")
