import os

from fastapi import FastAPI, HTTPException, WebSocket, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from .models import CreatorManager, DigitalCreator, Gender, Niche, SubscriptionTier, ContentType
from .content_manager import ContentManager
from .monetization import MonetizationManager
from .streaming import StreamingManager
from .interaction import InteractionManager
from .health_monitor import HealthMonitor
from .key_manager import AutonomousKeyManager
from .lyra_soul_manager import LyraSoulManager
from .ai_model_manager import AIModelManager

app = FastAPI(title="C.C. Autonomous AI Model Organization", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
creator_manager = CreatorManager()
content_manager = ContentManager()
streaming_manager = StreamingManager()
interaction_manager = InteractionManager()
health_monitor = HealthMonitor()
key_manager = AutonomousKeyManager()
lyra_soul_manager = LyraSoulManager()
ai_model_manager = AIModelManager()
INTERVENTION_ADMIN_TOKEN = os.getenv("INTERVENTION_ADMIN_TOKEN", "secret-dashboard-token")

# Placeholder for monetization - would need Stripe keys
# monetization_manager = MonetizationManager(stripe_secret_key="your_key")

class CreateCreatorRequest(BaseModel):
    name: str
    description: str
    gender: Gender
    niche: Niche
    appearance: dict
    voice_profile: str
    personality_traits: list
    social_media_handles: dict
    subscription_tiers: dict

class InteractRequest(BaseModel):
    message: str
    user_id: str
    context: Optional[dict] = {}

class AgentAccountRequest(BaseModel):
    agent_name: str
    niche: Optional[str] = None
    platforms: Optional[List[str]] = None
    include_porn_sites: Optional[bool] = True

class CreateAIModelRequest(BaseModel):
    base_name: str
    archetype: Optional[str] = None
    niche: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Welcome to C.C. Autonomous AI Model Organization"}

@app.get("/creators")
async def get_creators():
    return {"creators": list(creator_manager.creators.values())}

@app.get("/creators/{creator_id}")
async def get_creator(creator_id: str):
    creator = creator_manager.get_creator(creator_id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    return creator

@app.post("/creators")
async def create_creator(request: CreateCreatorRequest):
    creator = DigitalCreator(
        id=f"creator_{len(creator_manager.creators)}",
        name=request.name,
        description=request.description,
        gender=request.gender,
        niche=request.niche,
        appearance=request.appearance,
        voice_profile=request.voice_profile,
        personality_traits=request.personality_traits,
        social_media_handles=request.social_media_handles,
        subscription_tiers=request.subscription_tiers
    )
    creator_manager.add_creator(creator)
    return {"creator_id": creator.id, "message": "Creator created successfully"}

@app.post("/creators/{creator_id}/interact")
async def interact_with_creator(creator_id: str, request: InteractRequest):
    creator = creator_manager.get_creator(creator_id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")

    response = interaction_manager.generate_response(
        creator, request.message, request.user_id, request.context or {}
    )
    return {"response": response}

@app.get("/creators/{creator_id}/content")
async def get_creator_content(creator_id: str, subscriber_tier: SubscriptionTier = SubscriptionTier.FREE):
    creator = creator_manager.get_creator(creator_id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")

    content = content_manager.get_content_feed(creator, subscriber_tier)
    return {"content": content}

@app.post("/creators/{creator_id}/content/generate")
async def generate_content(creator_id: str, theme: str, content_type: str, is_premium: bool = False):
    creator = creator_manager.get_creator(creator_id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")

    content_type_enum = ContentType(content_type)

    post = await content_manager.generate_post(creator, theme, content_type_enum, is_premium)
    return {"post": post}

@app.post("/creators/{creator_id}/stream/start")
async def start_stream(creator_id: str, title: str, description: str = ""):
    creator = creator_manager.get_creator(creator_id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")

    stream = streaming_manager.start_stream(creator, title, description)
    return {"stream_id": stream.id, "message": "Stream started"}

@app.post("/creators/{creator_id}/stream/end")
async def end_stream(creator_id: str):
    streaming_manager.end_stream(creator_id)
    return {"message": "Stream ended"}

@app.get("/creators/{creator_id}/stream/stats")
async def get_stream_stats(creator_id: str):
    stats = streaming_manager.get_stream_stats(creator_id)
    return stats

@app.websocket("/ws/creators/{creator_id}/stream")
async def stream_websocket(websocket: WebSocket, creator_id: str):
    await websocket.accept()
    await streaming_manager.handle_websocket_connection(websocket, creator_id)

@app.get("/analytics/{creator_id}")
async def get_creator_analytics(creator_id: str):
    creator = creator_manager.get_creator(creator_id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")

    # Combine analytics from different managers
    analytics = {
        "subscriber_count": len(creator.subscribers),
        "content_count": len(creator.content_posts),
        "revenue": creator.revenue,
        "is_online": creator.is_online
    }

    return analytics

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return health_monitor.get_health_report()


def _verify_admin_token(x_admin_token: str = Header(..., alias="X-ADMIN-TOKEN")):
    if x_admin_token != INTERVENTION_ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized access to intervention dashboard")

@app.get("/interventions/tasks")
async def list_intervention_tasks(x_admin_token: str = Header(..., alias="X-ADMIN-TOKEN")):
    _verify_admin_token(x_admin_token)
    return {"tasks": key_manager.intervention_manager.get_tasks()}

@app.get("/interventions/tasks/{task_id}")
async def get_intervention_task(task_id: str, x_admin_token: str = Header(..., alias="X-ADMIN-TOKEN")):
    _verify_admin_token(x_admin_token)
    task = key_manager.intervention_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Intervention task not found")
    return task

@app.post("/interventions/tasks/{task_id}/resolve")
async def resolve_intervention_task(task_id: str, result: dict, x_admin_token: str = Header(..., alias="X-ADMIN-TOKEN")):
    _verify_admin_token(x_admin_token)
    task = key_manager.intervention_manager.resolve_task(task_id, result)
    if not task:
        raise HTTPException(status_code=404, detail="Intervention task not found")

    applied = key_manager.apply_intervention_result(task)
    return {
        "status": "resolved",
        "task": task,
        "applied": applied
    }

@app.get("/interventions/dashboard", response_class=HTMLResponse)
async def intervention_dashboard(x_admin_token: str = Header(..., alias="X-ADMIN-TOKEN")):
    _verify_admin_token(x_admin_token)
    tasks = key_manager.intervention_manager.get_tasks()
    rows = []
    for task in tasks:
        rows.append(f"<tr><td>{task['id']}</td><td>{task['service']}</td><td>{task.get('agent_name')}</td><td>{task.get('status')}</td><td>{task.get('created_at')}</td></tr>")
    html = f"""
    <html>
      <head><title>Intervention Dashboard</title></head>
      <body>
        <h1>Manual Intervention Tasks</h1>
        <p>Use the <code>X-ADMIN-TOKEN</code> header to access these endpoints.</p>
        <table border=1 cellpadding=6 cellspacing=0>
          <thead><tr><th>ID</th><th>Service</th><th>Agent</th><th>Status</th><th>Created</th></tr></thead>
          <tbody>{''.join(rows)}</tbody>
        </table>
      </body>
    </html>
    """
    return html

@app.get("/interventions/summary")
async def intervention_summary(x_admin_token: str = Header(..., alias="X-ADMIN-TOKEN")):
    _verify_admin_token(x_admin_token)
    return key_manager.intervention_manager.get_task_summary()

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with all metrics"""
    system_health = health_monitor.get_system_health()
    app_health = health_monitor.get_application_health(creator_manager, streaming_manager, content_manager.performance_optimizer)
    services = health_monitor.check_service_dependencies()

    return {
        "system": system_health,
        "application": app_health,
        "services": services,
        "alerts": health_monitor.alerts[-5:] if health_monitor.alerts else []
    }

@app.post("/keys/initialize")
async def initialize_keys():
    """Autonomously initialize all API keys"""
    result = await key_manager.initialize_system()
    if result:
        keys = result.get("keys", {})
        pending = result.get("pending_tasks", [])
        status = "success" if keys else "pending_manual_intervention"
        return {
            "status": status,
            "keys_acquired": len(keys),
            "services": list(keys.keys()),
            "pending_tasks": pending
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to initialize keys")

@app.post("/lyra/initialize")
def initialize_lyra_model():
    """Initialize the Lyra Soul AI framework separately from the system manager."""
    return lyra_soul_manager.initialize()

@app.get("/lyra/context")
def get_lyra_context(user_id: Optional[str] = None):
    """Return Lyra's system context for a specific user."""
    return lyra_soul_manager.get_soul_context(user_id)

@app.get("/lyra/summary")
def get_lyra_summary():
    """Return Lyra's voice summary and guideline overview."""
    return {
        "summary": lyra_soul_manager.get_lexicon_summary()
    }

@app.post("/lyra/refresh-visual")
def refresh_lyra_visual(allow_hair_length_change: bool = False):
    """Refresh Lyra's current visual profile."""
    return lyra_soul_manager.refresh_visual_profile(allow_hair_length_change=allow_hair_length_change)

@app.post("/lyra/donate")
def donate_to_lyra(user_id: str, amount: float, note: Optional[str] = None):
    """Record a donation and update Lyra's donor status."""
    return lyra_soul_manager.record_donation(user_id, amount, note)

@app.get("/lyra/donation-status/{user_id}")
def get_lyra_donation_status(user_id: str):
    """Return donation status for a user."""
    return lyra_soul_manager.get_donation_status(user_id)

@app.post("/models/create")
async def create_ai_model(request: CreateAIModelRequest):
    model = ai_model_manager.create_model(request.base_name, archetype=request.archetype, niche=request.niche)
    return {"status": "created", "model": model}

@app.get("/models/template")
def get_model_template():
    return ai_model_manager.framework.create_framework_template()

@app.get("/models")
def list_ai_models():
    return {"models": ai_model_manager.list_models()}

@app.get("/models/{model_id}")
def get_ai_model(model_id: str):
    model = ai_model_manager.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model

@app.delete("/models/{model_id}")
def delete_ai_model(model_id: str):
    if ai_model_manager.delete_model(model_id):
        return {"status": "deleted", "model_id": model_id}
    raise HTTPException(status_code=404, detail="Model not found")

@app.get("/keys/status")
async def get_key_status():
    """Get status of all API keys"""
    status = key_manager.get_key_status()
    return status

@app.post("/keys/rotate/{service}")
async def rotate_key(service: str):
    """Rotate API key for a specific service"""
    success = await key_manager.rotate_keys(service)
    if success:
        return {"status": "success", "message": f"{service} key rotated successfully"}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to rotate {service} key")

@app.post("/keys/validate/{service}")
async def validate_key(service: str):
    """Validate a specific API key"""
    keys = key_manager.load_keys_securely()
    if not keys or service not in keys:
        raise HTTPException(status_code=404, detail=f"No key found for {service}")

    is_valid = await key_manager.validate_api_key(service, keys[service])
    return {"service": service, "valid": is_valid}

@app.get("/keys/secure-info")
async def get_secure_key_info():
    """Get secure information about stored keys (without revealing actual keys)"""
    keys = key_manager.load_keys_securely()
    if not keys:
        return {"status": "no_keys_stored"}

    info = {}
    for service, key in keys.items():
        info[service] = {
            "length": len(key),
            "type": "api_key" if not service.startswith(("twitter_", "instagram_")) else "credential",
            "masked": f"{key[:4]}****{key[-4:]}" if len(key) > 8 else "****"
        }

    return {"status": "keys_available", "key_info": info}

@app.post("/accounts/autonomous-register")
async def autonomous_register_accounts(request: AgentAccountRequest):
    accounts = await key_manager.acquire_agent_accounts(
        request.agent_name,
        niche=request.niche,
        platforms=request.platforms,
        include_porn_sites=request.include_porn_sites,
    )
    key_manager.store_accounts_securely(accounts)
    return {"status": "success", "agent": request.agent_name, "accounts": accounts}

@app.get("/accounts/status")
async def get_account_status():
    return key_manager.get_account_status()

@app.post("/keys/initialize-with-accounts")
async def initialize_keys_and_accounts():
    result = await key_manager.initialize_system()
    if result:
        keys = result.get("keys", {})
        pending = result.get("pending_tasks", [])
        return {
            "status": "success" if keys else "pending_manual_intervention",
            "keys_acquired": len(keys),
            "services": list(keys.keys()),
            "pending_tasks": pending,
            "accounts": key_manager.get_account_status()
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to initialize keys and accounts")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)