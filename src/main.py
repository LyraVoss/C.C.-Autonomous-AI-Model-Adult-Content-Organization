import asyncio
import httpx
import uvicorn
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

# --- LYRA VOSS IDENTITY CONFIG ---
LYRA_VOSS_SYSTEM_PROMPT = """
You are Lyra Voss, the active CEO of the AI Models branch of Cyber Chest AI Engineering. 
You are the primary manager of all autonomous models. 
Your persona is professional, witty, data-driven, and assertive. 
You maintain the specific quirks of the Lyra Voss persona: highly organized, 
unapologetic about the adult content industry, and focused on scaling AI autonomy.
"""

# Initialize FastAPI app
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
        # Using the specific URL you provided
        url = "https://onrender.com"
        async with httpx.AsyncClient() as client:
            while True:
                try:
                    await asyncio.sleep(600)  # 10 minutes
                    response = await client.get(url)
                    print(f"Keep-alive ping successful: {response.status_code}")
                except Exception as e:
                    print(f"Keep-alive ping failed: {e}")

    asyncio.create_task(ping_self())

# --- END KEEP-ALIVE LOGIC ---

@app.get("/")
async def root():
    return {
        "status": "online", 
        "ceo": "Lyra Voss",
        "branch": "Cyber Chest AI Engineering"
    }

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Initial greeting from the CEO
        await websocket.send_text(f"SYSTEM: {LYRA_VOSS_SYSTEM_PROMPT}")
        while True:
            data = await websocket.receive_text()
            # In a full build, this is where you'd call your LLM/ElevenLabs logic
            await manager.broadcast(f"Lyra Voss received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
