import json
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from src.backend.schemas.state import CallState
from src.backend.config import settings
from src.logger import logger

# Initialize the LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1, api_key=settings.gemini_api_key)
chat_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7, api_key=settings.gemini_api_key)

def format_history(messages: list) -> list:
    """Convert state messages to LangChain message objects."""
    formatted = []
    for msg in messages:
        if msg["role"] == "user":
            formatted.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            formatted.append(AIMessage(content=msg["content"]))
    return formatted

def greeting_node(state: CallState) -> dict:
    """The initial greeting node."""
    logger.info(f"Executing greeting_node for session {state.get('session_id')}")
    
    prompt = "You are Aarav, an AI Energy expert from CIMET. Greet the user naturally, acknowledge they started comparing energy plans, and ask if they are moving into a new property or staying at their current address."
    
    messages = [SystemMessage(content=prompt)]
    response = chat_llm.invoke(messages)
    
    return {
        "messages": [{"role": "assistant", "content": response.content}],
        "current_node": "is_moving_node",
        "retry_count": 0
    }

class AskFieldNode:
    """A reusable node class for asking and extracting a specific field."""
    
    def __init__(self, field_name: str, extraction_model: type[BaseModel], next_node: str, prompt_context: str):
        self.field_name = field_name
        self.extraction_model = extraction_model
        self.next_node = next_node
        self.prompt_context = prompt_context
        # LLM bound with structured output
        self.extractor = llm.with_structured_output(self.extraction_model)

    def __call__(self, state: CallState) -> dict:
        logger.info(f"Executing {self.field_name} node for session {state.get('session_id')}")
        
        # 1. Has the user answered our previous question?
        last_message = state["messages"][-1] if state.get("messages") else None
        
        if last_message and last_message["role"] == "user":
            # Try to extract the field from the entire conversation history
            history = format_history(state["messages"])
            extraction_prompt = SystemMessage(content=f"Extract the requested information based on the conversation. We are looking for: {self.prompt_context}")
            
            try:
                # Run extraction
                result = self.extractor.invoke([extraction_prompt] + history)
                
                # Check if the field was actually extracted (not None)
                extracted_dict = result.model_dump()
                if extracted_dict.get(self.field_name) is not None:
                    # Successfully extracted!
                    logger.info(f"Successfully extracted {self.field_name}: {extracted_dict[self.field_name]}")
                    
                    # Update fields
                    new_fields = state.get("extracted_fields", {}).copy()
                    new_fields.update(extracted_dict)
                    
                    # Generate natural transition to the next field (if not complete)
                    transition_prompt = f"The user just provided their {self.field_name}. Acknowledge it briefly and naturally ask the next question: {self._get_next_question()}"
                    response = chat_llm.invoke([SystemMessage(content=transition_prompt)] + history)
                    
                    return {
                        "extracted_fields": new_fields,
                        "current_node": self.next_node,
                        "retry_count": 0,
                        "messages": [{"role": "assistant", "content": response.content}]
                    }
            except Exception as e:
                logger.error(f"Extraction failed for {self.field_name}: {str(e)}")
        
        # 2. Ask or re-ask the question
        retry_count = state.get("retry_count", 0)
        if retry_count > 2:
            # Too many retries, escalate
            return {
                "needs_handoff": True,
                "handoff_reason": f"Failed to collect {self.field_name} after 3 attempts.",
                "current_node": "handoff_node"
            }
            
        ask_prompt = f"Ask the user: {self.prompt_context}. Be polite and concise."
        if retry_count > 0:
            ask_prompt = f"The user didn't provide a clear answer. Politely re-ask: {self.prompt_context}"
            
        response = chat_llm.invoke([SystemMessage(content=ask_prompt)] + format_history(state.get("messages", [])))
        
        return {
            "retry_count": retry_count + 1,
            "messages": [{"role": "assistant", "content": response.content}]
        }
        
    def _get_next_question(self) -> str:
        # Simple mapping for natural transitions
        mapping = {
            "address_node": "What is the full address of the property?",
            "fuel_type_node": "Are you looking for Electricity, Gas, or Both?",
            "has_solar_node": "Does the property have solar panels?",
            "has_life_support_node": "Does anyone at the property rely on life support equipment?",
            "concession_card_node": "Do you hold a valid government concession or pensioner card?",
            "complete_journey": "No more questions, let them know you are pulling up the best plans now."
        }
        return mapping.get(self.next_node, "Next question.")

def handoff_node(state: CallState) -> dict:
    """Handles the handoff logic."""
    reason = state.get("handoff_reason", "Customer requested human agent.")
    logger.warning(f"HANDOFF TRIGGERED. Reason: {reason}. Collected fields: {state.get('extracted_fields')}")
    
    return {
        "messages": [{"role": "assistant", "content": "I completely understand. Let me transfer you to one of our human energy experts who can help you further. Please hold on a moment."}],
        "current_node": "handoff_node"
    }

def complete_node(state: CallState) -> dict:
    """Ends the journey."""
    logger.info(f"Journey completed for session {state.get('session_id')}. Fields: {state.get('extracted_fields')}")
    return {
        "messages": [{"role": "assistant", "content": "I've got all the details I need. I'm generating your personalized energy comparison now!"}],
        "current_node": "end"
    }
