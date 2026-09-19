from pydantic import BaseModel
from typing import List, Optional

class CustomerResponse(BaseModel):
    name: str
    phone: str
    journey: str
    status: str

class JourneyResponse(BaseModel):
    moving: Optional[bool]
    address: Optional[str]
    fuel_type: Optional[str]
    solar: Optional[bool]
    life_support: Optional[bool]
    concession: Optional[bool]

class MessageResponse(BaseModel):
    speaker: str
    text: str

class WorkspaceResponse(BaseModel):
    customer: CustomerResponse
    journey_data: JourneyResponse
    summary: str
    transcript: List[MessageResponse]
    status: str

class LeadListResponse(BaseModel):
    session_id: str
    customer: str
    phone: str
    status: str
    reason: Optional[str]
    journey: str
