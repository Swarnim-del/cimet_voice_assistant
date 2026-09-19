import asyncio
import os
import sys

# Add src to sys path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from src.backend.repo.database import db, Base
from src.backend.repo.models import Customer, CallSession, ConversationMessage, JourneyData  # noqa

from sqlalchemy import text

async def init_db():
    async with db.engine.begin() as conn:
        print("Dropping schema...")
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO cimet_user"))
        print("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(init_db())
