from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"

class Niche(str, Enum):
    DOMINANT = "dominant"
    SUBMISSIVE = "submissive"
    FETISH = "fetish"
    ROLEPLAY = "roleplay"
    BDSM = "bdsm"
    # Add more as needed

class SubscriptionTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    VIP = "vip"

class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    LIVE_STREAM = "live_stream"

class ContentPost(BaseModel):
    id: str
    creator_id: str
    type: ContentType
    title: str
    description: str
    content_url: Optional[str]
    thumbnail_url: Optional[str]
    is_premium: bool = False
    required_tier: SubscriptionTier = SubscriptionTier.FREE
    created_at: datetime
    likes: int = 0
    comments: List[Dict] = []

class Subscriber(BaseModel):
    id: str
    username: str
    email: str
    tier: SubscriptionTier
    subscribed_at: datetime
    last_active: datetime
    preferences: Dict[str, Any] = {}

class DigitalCreator(BaseModel):
    id: str
    name: str
    description: str
    gender: Gender
    niche: Niche
    appearance: Dict[str, str]  # face, body, hair, piercings, tattoos, etc.
    voice_profile: str  # ElevenLabs voice ID or similar
    personality_traits: List[str]
    social_media_handles: Dict[str, str]  # platform: handle
    subscription_tiers: Dict[SubscriptionTier, Dict[str, Any]]  # pricing, benefits
    subscribers: List[Subscriber] = []
    content_posts: List[ContentPost] = []
    is_online: bool = False
    last_active: Optional[datetime] = None
    revenue: float = 0.0
    analytics: Dict[str, Any] = {}

    def generate_content(self, prompt: str, content_type: ContentType) -> ContentPost:
        # Placeholder for content generation
        return ContentPost(
            id=f"{self.id}_{len(self.content_posts)}",
            creator_id=self.id,
            type=content_type,
            title=f"Generated {content_type} for {self.name}",
            description=f"AI-generated content: {prompt}",
            created_at=datetime.now()
        )

    def interact_with_fan(self, message: str, fan_id: str) -> str:
        # Placeholder for fan interaction
        return f"{self.name} responds to {fan_id}: {message}"

    def post_to_social_media(self, platform: str, content: str):
        # Placeholder for social media posting
        print(f"Posting to {platform}: {content}")

    def add_subscriber(self, subscriber: Subscriber):
        self.subscribers.append(subscriber)

    def remove_subscriber(self, subscriber_id: str):
        self.subscribers = [s for s in self.subscribers if s.id != subscriber_id]

class CreatorManager:
    def __init__(self):
        self.creators: Dict[str, DigitalCreator] = {}

    def add_creator(self, creator: DigitalCreator):
        self.creators[creator.id] = creator

    def get_creator(self, creator_id: str) -> Optional[DigitalCreator]:
        return self.creators.get(creator_id)

    def get_online_creators(self) -> List[DigitalCreator]:
        return [creator for creator in self.creators.values() if creator.is_online]

    def set_creator_online(self, creator_id: str, online: bool):
        if creator := self.get_creator(creator_id):
            creator.is_online = online
            creator.last_active = datetime.now() if online else None

    def get_creators_by_niche(self, niche: Niche) -> List[DigitalCreator]:
        return [creator for creator in self.creators.values() if creator.niche == niche]