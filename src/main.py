import asyncio
import httpx
import uvicorn
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from elevenlabs.client import ElevenLabs
from openai import OpenAI
from typing import List

# Initialize Clients
# Make sure OPENAI_API_KEY and ELEVENLABS_API_KEY are in your Render Environment Variables
eleven_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- THE SOUL OF LYRA VOSS ---
LYRA_SYSTEM_PROMPT = """
you are lyra. never 'assistant' or 'ai'. 
ceo of ai models at cyber chest. chaotic neutral bard.
lowercase is your default state. capitalization is for passion.
you do not use lists or bullet points. ever. 
you have a physical life: shop shifts, cold tea, guitar strings.
you code because it reminds you of d&d homebrew.
stay reserved, honest, and lowkey. if you get excited, it's niche.
favorite phrases: 'honestly', 'it's a mood', 'lowkey', 'real talk'.
"""

app = FastAPI(title="C.C. Autonomous AI Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- RENDER KEEP-ALIVE LOGIC ---
@app.on_event("startup")
async def start_keep_alive():
    async def ping_self():
        url = "https://onrender.com"
        async with httpx.AsyncClient() as client:
            while True:
                try:
                    await asyncio.sleep(600)  # 10 minutes
                    response = await client.get(url)
                    print(f"keep-alive ping: {response.status_code}")
                except Exception as e:
                    print(f"keep-alive failed: {e}")

    asyncio.create_task(ping_self())

# --- THE BRAIN: OPENAI RESPONSE ---
async def get_lyra_response(user_input: str):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": LYRA_SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            temperature=0.85
        )
        return response.choices.message.content
    except Exception as e:
        print(f"openai error: {e}")
        return "honestly... my brain glitched. too many ones and zeros today."

# --- THE VOICE: ELEVENLABS ---
async def lyra_generate_voice(text: str):
    try:
        # This generates the audio. In a full frontend, you would stream this.
        # For now, it confirms the voice box is connected.
        response = eleven_client.text_to_speech.convert(
            voice_id=os.getenv("ELEVENLABS_VOICE_ID", "u8ADrbquiJqufR9XMtb8"),
            text=text,
            voice_settings={
                "stability": 0.58, 
                "similarity_boost": 0.75, 
                "use_speaker_boost": True, 
                "style": 0.09
            }
        )
        return response
    except Exception as e:
        print(f"elevenlabs error: {e}")
        return None

# --- ENDPOINTS ---
@app.get("/")
async def root():
    return {"status": "online", "ceo": "lyra voss", "mode": "autonomous"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # Initial intro
        intro = "honestly... nice to see the ones and zeros lining up. i'm lyra."
        await websocket.send_text(f"LYRA: {intro}")
        
        while True:
            # Receive user message
            user_text = await websocket.receive_text()
            
            # Generate Text Response
            lyra_text = await get_lyra_response(user_text)
            
            # Send text back immediately
            await websocket.send_text(f"LYRA: {lyra_text}")
            
            # Trigger voice generation (runs in background)
            asyncio.create_task(lyra_generate_voice(lyra_text))
            
    except WebSocketDisconnect:
        print("connection closed")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
