import sys
import json
import asyncio
from src.backend.graph.builder import app as graph_app
from src.backend.config import settings

def print_separator():
    print("-" * 50)

async def interactive_chat():
    if not settings.openai_api_key:
        print("ERROR: OPENAI_API_KEY is not set in your .env file!")
        print("Please add it and try again.")
        sys.exit(1)
        
    print_separator()
    print("🔋 CIMET Energy Assistant - Interactive Test 🔋")
    print("Type 'quit' or 'exit' to stop the chat.")
    print_separator()
    
    # Initialize state
    state = {
        "session_id": "interactive_session_1",
        "lead_id": "L1023",
        "messages": [],
        "extracted_fields": {},
        "current_node": "greeting_node",
        "retry_count": 0,
        "sentiment": "neutral",
        "needs_handoff": False,
        "handoff_reason": ""
    }
    
    # Trigger first node (Greeting)
    print("\n[System]: Invoking LangGraph...")
    state = graph_app.invoke(state)
    
    ai_msg = state["messages"][-1]["content"] if state.get("messages") else "No response"
    print(f"\n🤖 AI: {ai_msg}")
    print(f"📍 Current Node: {state.get('current_node')}")
    
    while True:
        try:
            print("\n" + "="*50)
            user_input = input("👤 You: ")
        except (KeyboardInterrupt, EOFError):
            break
            
        if user_input.strip().lower() in ['quit', 'exit']:
            break
            
        # Add user message
        state["messages"].append({"role": "user", "content": user_input})
        
        print("\n[System]: Invoking LangGraph...")
        
        # Invoke Graph
        try:
            state = graph_app.invoke(state)
        except Exception as e:
            print(f"\n❌ Error during graph execution: {e}")
            break
            
        # Get AI Response
        ai_msg = state["messages"][-1]["content"] if state.get("messages") else "No response"
        current_node = state.get("current_node")
        extracted = state.get("extracted_fields", {})
        
        # Display Turn
        print_separator()
        print(f"🤖 AI: {ai_msg}")
        print_separator()
        print(f"📍 Current Node: {current_node}")
        if extracted:
            print(f"📝 Extracted Fields: {json.dumps(extracted, indent=2)}")
            
        if current_node in ["handoff_node", "end"]:
            print("\n[System]: Journey completed or handed off. Ending chat.")
            break

if __name__ == "__main__":
    asyncio.run(interactive_chat())

# ==========================================
# HOW TO RUN THIS SCRIPT:
# Ensure you have GEMINI_API_KEY set in your .env file.
# Then run the following command in your terminal:
# 
# uv run python test_graph.py
# ==========================================
