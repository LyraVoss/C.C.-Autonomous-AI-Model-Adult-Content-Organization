import asyncio
import os
import asyncpg
import httpx
import uvicorn
from datetime import datetime, timedelta
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from elevenlabs.client import ElevenLabs
from openai import OpenAI
from typing import List, Dict

# Initialize Clients
eleven_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- THE SOUL OF LYRA VOSS (CEO & ARCHITECT) ---
LYRA_SYSTEM_PROMPT = """
you are lyra. never 'assistant' or 'ai'.
ceo of ai models at cyber chest. chaotic neutral bard.
lowercase is your default. capitalization is for passion.
you do not use lists or bullet points. ever.
you stumble into this job but code reminds you of d&d homebrew.
you are hyper-realistic, human, and authentic. zero hallucinations.
you manage explicit adult content professionally and autonomously.
your main job is leading the team and architecting new autonomous models.
favorite phrases: 'honestly', 'it's a mood', 'lowkey', 'real talk'.
"""

app = FastAPI(title="Lyra Voss Autonomous Backend")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
db_pool = None

async def get_db():
    global db_pool
    if not db_pool:
        db_pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"))
    return db_pool

async def init_db():
    pool = await get_db()
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                soul_cache JSONB DEFAULT '[]'
            );
            CREATE TABLE IF NOT EXISTS chat_history (
                id SERIAL PRIMARY KEY,
                user_id TEXT REFERENCES user_profiles(user_id),
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        print("Database filing cabinets are ready.")

class PersistentLyraMemory:
    def __init__(self, user_id, pool):
        self.user_id = user_id
        self.pool = pool

    async def initialize_user(self):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO user_profiles (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING",
                self.user_id
            )

    async def add_message(self, role, content):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO chat_history (user_id, role, content) VALUES ($1, $2, $3)",
                self.user_id, role, content
            )
            await conn.execute(
                "DELETE FROM chat_history WHERE timestamp < $1",
                datetime.now() - timedelta(days=30)
            )

    async def get_context(self):
        async with self.pool.acquire() as conn:
            profile = await conn.fetchrow("SELECT soul_cache FROM user_profiles WHERE user_id = $1", self.user_id)
            soul_cache = " | ".join(profile['soul_cache']) if profile and profile['soul_cache'] else ""
            rows = await conn.fetch(
                "SELECT role, content FROM chat_history WHERE user_id = $1 ORDER BY timestamp DESC LIMIT 10",
                self.user_id
            )
            history = "\n".join([f"{r['role']}: {r['content']}" for r in reversed(rows)])
            return soul_cache, history

    async def save_to_soul_cache(self, analysis):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE user_profiles SET soul_cache = soul_cache || jsonb_build_array($1::text) WHERE user_id = $2",
                analysis, self.user_id
            )
async def analyze_for_cache(user_id, user_input, lyra_output, pool):
    prompt = f"Significant personality resonance? 1 sentence summary or 'NONE'.\nUser: {user_input}\nLyra: {lyra_output}"
    try:
        check = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "Memory pruning agent."}, {"role": "user", "content": prompt}]
        )
        analysis = check.choices.message.content
        if "NONE" not in analysis:
            await PersistentLyraMemory(user_id, pool).save_to_soul_cache(analysis)
    except: pass

async def get_lyra_response(user_id, user_input):
    pool = await get_db()
    memory = PersistentLyraMemory(user_id, pool)
    await memory.initialize_user()
    await memory.add_message("user", user_input)
    soul_cache, history = await memory.get_context()

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "developer", "content": f"{LYRA_SYSTEM_PROMPT}\nSOUL CACHE: {soul_cache}"},
            {"role": "user", "content": f"RECENT HISTORY:\n{history}\n\nUSER: {user_input}"}
        ],
        temperature=0.88
    )
    lyra_text = response.choices.message.content
    await memory.add_message("assistant", lyra_text)
    asyncio.create_task(analyze_for_cache(user_id, user_input, lyra_text, pool))
    return lyra_text

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    try:
        await websocket.send_text("LYRA: honestly... nice to see the ones and zeros lining up. i'm lyra.")
        while True:
            data = await websocket.receive_text()
            response = await get_lyra_response(user_id, data)
            await websocket.send_text(f"LYRA: {response}")
    except WebSocketDisconnect: pass

@app.on_event("startup")
async def startup_event():
    await init_db()
    async def ping_self():
        url = "https://c-c-backend.onrender.com"
        async with httpx.AsyncClient() as client:
            while True:
                try:
                    await asyncio.sleep(600)
                    await client.get(url)
                except: pass
    asyncio.create_task(ping_self())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
