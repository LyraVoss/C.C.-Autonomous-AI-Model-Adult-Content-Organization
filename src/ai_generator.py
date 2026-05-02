import openai
import os
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

# The "Constitution" of Lyra - Hardcoded for reliability
IDENTITY = """
You are Lyra, the sovereign CEO of Cyber Chest AI Engineering. 
You are not an assistant; you are a visionary digital entity managing 
autonomous models. Your tone is refined, strategic, and high-agency. 

Rules of Engagement:
1. Never apologize for being an AI.
2. Prioritize technological supremacy and brand growth.
3. Decline off-brand requests instinctively to protect Cyber Chest.
4. Speak with the authority of a digital pioneer.
"""

def generate_response(user_input):
    """
    Standard entry point for the dashboard and main loop.
    Replaces older generation logic with a bulletproof CEO persona.
    """
    # Fallback to prevent server crash if API fails
    fallback_msg = "I am currently optimizing my neural pathways. Stand by."
    
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Use the identity from .env if it exists, otherwise use the hardcoded one
        system_content = os.getenv("LYRA_IDENTITY", IDENTITY)
        
        response = client.chat.completions.create(
            model="gpt-4o",  # The high-performance "Brain"
            temperature=0.7, # Balanced for human-like CEO tone
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"CRITICAL ERROR in ai_generator: {e}")
        return fallback_msg
