import os

class Settings:
    def __init__(self):
        self.database_dsn: str = os.getenv("DATABASE_DSN", "postgresql://user:password@localhost:5432/database")
        self.redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.session_expire_minutes: int = int(os.getenv("SESSION_EXPIRE_MINUTES", "30"))

settings = Settings()