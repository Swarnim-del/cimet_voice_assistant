import json
from pydantic import BaseModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from src.backend.schemas.state import CallState
from src.backend.config import settings
from src.logger import logger
from src.backend.graph.script_data import PITCH_SCRIPT

# Initialize the LLM
llm = ChatOpenAI(model="gpt-5-mini", temperature=0.1, api_key=settings.openai_api_key)
chat_llm = ChatOpenAI(model="gpt-5-mini", temperature=0.7, api_key=settings.openai_api_key)

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
    
    script = PITCH_SCRIPT.get("greeting", {})
    greeting_text = script.get("prompt", "Hello, how can I help you?")
    
    prompt = f"""
You are Aarav, an AI energy expert at CIMET.
The customer has requested an energy comparison but hasn't completed it.

Your goal for this first message:
1. Introduce yourself warmly and professionally.
2. Acknowledge they were comparing energy plans.
3. Strongly assure them that their data and privacy are strictly protected and kept secure.
4. Ask the very first question EXACTLY as written: "{greeting_text}"

Keep it conversational, trustworthy, and engaging. DO NOT ask more than one question.

Output ONLY the exact text you want to say to the customer.
"""
    
    # Gemini requires at least one HumanMessage in the conversation history
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content="Start the conversation.")
    ]
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
                    next_script = PITCH_SCRIPT.get(self.next_node.replace("_node", ""), {})
                    next_question = next_script.get("prompt", self._get_next_question())
                    
                    transition_prompt = f"The user just provided their {self.field_name}. Acknowledge it briefly and naturally ask the next question exactly as written: {next_question}"
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
            
        script = PITCH_SCRIPT.get(self.field_name, {})
        exact_question = script.get("prompt", self.prompt_context)
        
        ask_prompt = f"Ask the user exactly: '{exact_question}'. Be polite and concise."
        if retry_count > 0:
            ask_prompt = f"The user didn't provide a clear answer. Politely re-ask: '{exact_question}'"
            
        response = chat_llm.invoke([SystemMessage(content=ask_prompt)] + format_history(state.get("messages", [])))
        
        return {
            "retry_count": retry_count + 1,
            "messages": [{"role": "assistant", "content": response.content}]
        }
        
    def _get_next_question(self) -> str:
        return "Next question."

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
