import operator
from typing import TypedDict, Annotated, List, Dict, Any
from pydantic import BaseModel, Field

class EnergyJourneyFields(BaseModel):
    is_moving: bool | None = Field(None, description="Is the customer moving into a new property, or staying at their current address?")
    address: str | None = Field(None, description="The full service address for the energy connection.")
    fuel_type: str | None = Field(None, description="Electricity, Gas, or Both.")
    has_solar: bool | None = Field(None, description="Does the property have solar panels installed?")
    has_life_support: bool | None = Field(None, description="Does anyone at the property rely on life support equipment? (Crucial AU regulatory field)")
    concession_card: bool | None = Field(None, description="Does the customer hold a valid government concession or pensioner card?")

class CallState(TypedDict):
    session_id: str
    lead_id: str
    
    # We will just append new messages (dictionaries of role/content for simplicity or BaseMessage)
    messages: Annotated[List[Dict[str, str]], operator.add]
    
    extracted_fields: Dict[str, Any]
    current_node: str
    retry_count: int
    
    sentiment: str
    needs_handoff: bool
    handoff_reason: str
