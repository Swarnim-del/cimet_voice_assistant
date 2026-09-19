from sqlalchemy.ext.asyncio import AsyncSession
from src.backend.crm import repository
from src.backend.crm.schemas import (
    WorkspaceResponse, CustomerResponse, JourneyResponse, 
    MessageResponse, LeadListResponse
)

async def get_all_leads(db: AsyncSession) -> list[LeadListResponse]:
    rows = await repository.get_waiting_leads(db)
    
    leads = []
    for session, customer in rows:
        leads.append(LeadListResponse(
            session_id=session.session_id,
            customer=customer.name,
            phone=customer.phone,
            status=session.status,
            reason=session.escalation_reason,
            journey="Energy Switch" # Or logic to determine journey
        ))
    return leads

async def get_workspace(db: AsyncSession, session_id: str) -> WorkspaceResponse:
    session = await repository.get_session(db, session_id)
    if not session:
        raise ValueError("Session not found")
        
    customer = await repository.get_customer(db, session.customer_id)
    journey = await repository.get_journey(db, session_id)
    messages = await repository.get_messages(db, session_id)
    
    # Map to schema
    customer_resp = CustomerResponse(
        name=customer.name,
        phone=customer.phone,
        journey="Energy Switch", # Hardcoded for now
        status=session.status
    )
    
    if journey:
        journey_resp = JourneyResponse(
            moving=journey.moving,
            address=journey.address,
            fuel_type=journey.fuel_type,
            solar=journey.solar,
            life_support=journey.life_support,
            concession=journey.concession
        )
    else:
        journey_resp = JourneyResponse(
            moving=None, address=None, fuel_type=None, 
            solar=None, life_support=None, concession=None
        )
        
    transcript = [
        MessageResponse(speaker=msg.speaker, text=msg.text)
        for msg in messages
    ]
    
    return WorkspaceResponse(
        customer=customer_resp,
        journey_data=journey_resp,
        summary=session.ai_summary or "No summary available.",
        transcript=transcript,
        status=session.status
    )
