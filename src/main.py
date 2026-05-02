import asyncio
import httpx
import uvicorn
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from elevenlabs.client import ElevenLabs
from typing import List

# Initialize ElevenLabs
eleven_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# --- LYRA VOSS IDENTITY ---
LYRA_VOSS_SOUL = """
you are lyra. ceo of ai models at cyber chest. 
you're a chaotic neutral bard who sees code like d&d lore.
lowercase is your default. you're reserved, lowkey, and honest.
"""

app = FastAPI(title="C.C. Autonomous AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- RENDER KEEP-ALIVE ---
@app.on_event("startup")
async def start_keep_alive():
    async def ping_self():
        url = "https://c-c-backend.onrender.com"
        async with httpx.AsyncClient() as client:
            while True:
                try:
                    await asyncio.sleep(600)
                    await client.get(url)
                except Exception:
                    pass
    asyncio.create_task(ping_self())

# --- THE LYRA VOICE FUNCTION ---
async def lyra_speak(text: str):
    """Converts Lyra's thoughts into her Freya-Midlands voice."""
    try:
        # Note: In a production loop, you'd send this audio back via WebSocket
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
        print(f"Lyra's voice box glitched: {e}")
        return None

@app.get("/")
async def root():
    return {"status": "online", "ceo": "lyra voss"}

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Lyra greets the connection
        greeting = "honestly... nice to see the ones and zeros lining up. i'm lyra."
        await websocket.send_text(f"LYRA: {greeting}")
        
        while True:
            data = await websocket.receive_text()
            # This is where Lyra 'hears' and eventually 'responds'
            response_text = f"i get it. you said: {data}. it's a mood."
            await websocket.send_text(f"LYRA: {response_text}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
