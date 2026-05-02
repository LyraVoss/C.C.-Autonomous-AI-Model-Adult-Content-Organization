import asyncio
import httpx
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

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
        url = "https://c-c-backend.onrender.com"
        async with httpx.AsyncClient() as client:
            while True:
                try:
                    # Wait 10 minutes (600 seconds)
                    await asyncio.sleep(600)
                    response = await client.get(url)
                    print(f"Keep-alive ping successful: {response.status_code}")
                except Exception as e:
                    print(f"Keep-alive ping failed: {e}")

    # Start the ping loop in the background
    asyncio.create_task(ping_self())
# --- END KEEP-ALIVE LOGIC ---

# Simple health check endpoint
@app.get("/")
async def root():
    return {"status": "online", "message": "C.C. Autonomous AI Model is active"}

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
        while True:
            data = await websocket.receive_text()
            # Echo back for testing or process logic here
            await manager.broadcast(f"C.C. received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    # Render uses the PORT environment variable
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
