from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from src.backend.repo.database import db

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in db.get_session():
        yield session
