from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from src.backend.schemas.state import CallState
from src.backend.graph.nodes import (
    greeting_node, 
    AskFieldNode, 
    handoff_node,
    complete_node
)

# 1. Define specific single-field schemas for each node
class IsMovingSchema(BaseModel):
    is_moving: bool = Field(description="True if moving into a new property, False if staying at current address.")

class AddressSchema(BaseModel):
    address: str = Field(description="The full service address for the energy connection.")

class FuelTypeSchema(BaseModel):
    fuel_type: str = Field(description="Electricity, Gas, or Both.")

class HasSolarSchema(BaseModel):
    has_solar: bool = Field(description="Does the property have solar panels installed?")

class LifeSupportSchema(BaseModel):
    has_life_support: bool = Field(description="Does anyone at the property rely on life support equipment?")

class ConcessionCardSchema(BaseModel):
    concession_card: bool = Field(description="Does the customer hold a valid government concession or pensioner card?")


# 2. Instantiate the field nodes
is_moving_node = AskFieldNode(
    field_name="is_moving",
    extraction_model=IsMovingSchema,
    next_node="address_node",
    prompt_context="Find out if the customer is moving into a new property or staying at their current address."
)

address_node = AskFieldNode(
    field_name="address",
    extraction_model=AddressSchema,
    next_node="fuel_type_node",
    prompt_context="Get the full address of the property where they need the energy connected."
)

fuel_type_node = AskFieldNode(
    field_name="fuel_type",
    extraction_model=FuelTypeSchema,
    next_node="has_solar_node",
    prompt_context="Find out if they want to compare Electricity, Gas, or Both."
)

has_solar_node = AskFieldNode(
    field_name="has_solar",
    extraction_model=HasSolarSchema,
    next_node="has_life_support_node",
    prompt_context="Find out if the property has solar panels installed."
)

has_life_support_node = AskFieldNode(
    field_name="has_life_support",
    extraction_model=LifeSupportSchema,
    next_node="concession_card_node",
    prompt_context="Crucial: Find out if anyone at the property relies on life support equipment."
)

concession_card_node = AskFieldNode(
    field_name="concession_card",
    extraction_model=ConcessionCardSchema,
    next_node="complete_journey",
    prompt_context="Find out if the customer holds a valid government concession or pensioner card."
)

# 3. Build the StateGraph
workflow = StateGraph(CallState)

# Add Nodes
workflow.add_node("greeting_node", greeting_node)
workflow.add_node("is_moving_node", is_moving_node)
workflow.add_node("address_node", address_node)
workflow.add_node("fuel_type_node", fuel_type_node)
workflow.add_node("has_solar_node", has_solar_node)
workflow.add_node("has_life_support_node", has_life_support_node)
workflow.add_node("concession_card_node", concession_card_node)
workflow.add_node("handoff_node", handoff_node)
workflow.add_node("complete_journey", complete_node)

# Add Edges (Routing is primarily handled via the state's current_node, 
# but LangGraph needs structural edges. We can use conditional edges based on state["current_node"])
def route_next(state: CallState) -> str:
    if state.get("needs_handoff"):
        return "handoff_node"
    
    current = state.get("current_node")
    if not current:
        return "greeting_node"
    
    # Life Support triggers immediate handoff for this hackathon
    if state.get("extracted_fields", {}).get("has_life_support") is True:
        state["handoff_reason"] = "Life Support requires specialized human assistance."
        return "handoff_node"
        
    return current

# Set the entry point
workflow.set_entry_point("greeting_node")

# All nodes should route through the conditional edge to determine next steps dynamically
workflow.add_conditional_edges("greeting_node", route_next)
workflow.add_conditional_edges("is_moving_node", route_next)
workflow.add_conditional_edges("address_node", route_next)
workflow.add_conditional_edges("fuel_type_node", route_next)
workflow.add_conditional_edges("has_solar_node", route_next)
workflow.add_conditional_edges("has_life_support_node", route_next)
workflow.add_conditional_edges("concession_card_node", route_next)

# Terminal edges
workflow.add_edge("handoff_node", END)
workflow.add_edge("complete_journey", END)

# Compile
app = workflow.compile()
