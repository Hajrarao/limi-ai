from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from music_engine import generate_music
import re
import os

# --- LangChain: Natural language → room state → music ---

MUSIC_SYSTEM_PROMPT = """You are Limi AI's music controller for smart ambient systems.
Based on the user's request, determine the room state and music parameters.

Available room states: focus, social, energetic, calm

Respond ONLY in this exact format (no other text):
STATE: <state>
REASON: <one sentence why>

Examples:
- "I need to concentrate" → STATE: focus
- "We're having a party" → STATE: social  
- "Make it more upbeat" → STATE: energetic
- "Help me relax" → STATE: calm
"""

def parse_llm_response(response: str) -> str:
    """Extract room state from LLM response."""
    match = re.search(r"STATE:\s*(\w+)", response, re.IGNORECASE)
    if match:
        state = match.group(1).lower()
        valid_states = ["focus", "social", "energetic", "calm"]
        return state if state in valid_states else "focus"
    return "focus"

def music_controller(user_prompt: str, use_mock: bool = True) -> dict:
    """
    Takes natural language prompt → generates appropriate music.
    use_mock=True: uses simple keyword matching (no API key needed for demo)
    use_mock=False: uses real LangChain + OpenAI
    """
    
    if use_mock:
        # Keyword-based mock for demo (works without API key)
        prompt_lower = user_prompt.lower()
        if any(w in prompt_lower for w in ["focus", "study", "concentrate", "work", "quiet"]):
            state = "focus"
        elif any(w in prompt_lower for w in ["party", "social", "friends", "fun", "gather"]):
            state = "social"
        elif any(w in prompt_lower for w in ["energetic", "upbeat", "fast", "dance", "pump"]):
            state = "energetic"
        elif any(w in prompt_lower for w in ["relax", "calm", "sleep", "rest", "peace"]):
            state = "calm"
        else:
            state = "focus"
        reason = f"Detected '{state}' intent from prompt keywords"
    else:
        # Real LangChain pipeline
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
        prompt = ChatPromptTemplate.from_messages([
            ("system", MUSIC_SYSTEM_PROMPT),
            ("human", "{user_input}")
        ])
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"user_input": user_prompt})
        state = parse_llm_response(response)
        reason = response
    
    output_file = f"{state}_generated.mid"
    generate_music(room_state=state, output_path=output_file)
    
    return {
        "user_prompt": user_prompt,
        "detected_state": state,
        "reason": reason,
        "output_file": output_file,
        "status": "success"
    }

if __name__ == "__main__":
    # Test the LangChain music controller
    test_prompts = [
        "Make the music more energetic, we're having a team celebration!",
        "I need to focus on this report, something calm please",
        "Everyone is arriving for the party, make it social",
    ]
    
    for prompt in test_prompts:
        result = music_controller(prompt, use_mock=True)
        print(f"\nPrompt: '{result['user_prompt']}'")
        print(f"→ State: {result['detected_state']} | File: {result['output_file']}")
