from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, desc
from src.backend.repo.models import Customer, CallSession, JourneyData, ConversationMessage

async def get_waiting_leads(db: AsyncSession):
    stmt = (
        select(CallSession, Customer)
        .join(Customer, CallSession.customer_id == Customer.id)
        .where(CallSession.status != "COMPLETED")
        .order_by(desc(CallSession.created_at))
    )
    result = await db.execute(stmt)
    return result.all()

async def get_session(db: AsyncSession, session_id: str) -> CallSession:
    stmt = (
        select(CallSession)
        .where(CallSession.session_id == session_id)
    )
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_customer(db: AsyncSession, customer_id: str) -> Customer:
    stmt = select(Customer).where(Customer.id == customer_id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_journey(db: AsyncSession, session_id: str) -> JourneyData:
    stmt = select(JourneyData).where(JourneyData.session_id == session_id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_messages(db: AsyncSession, session_id: str):
    stmt = (
        select(ConversationMessage)
        .where(ConversationMessage.session_id == session_id)
        .order_by(ConversationMessage.created_at)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_status(db: AsyncSession, session_id: str, new_status: str):
    stmt = (
        update(CallSession)
        .where(CallSession.session_id == session_id)
        .values(status=new_status)
    )
    await db.execute(stmt)
    await db.commit()
