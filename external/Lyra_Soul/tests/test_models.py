import pytest
from src.models import DigitalCreator, CreatorManager, Gender, Niche, SubscriptionTier, ContentPost, ContentType, Subscriber
from datetime import datetime

def test_digital_creator_creation():
    creator = DigitalCreator(
        id="test_creator",
        name="Test Creator",
        description="A test AI creator",
        gender=Gender.FEMALE,
        niche=Niche.DOMINANT,
        appearance={"hair": "blonde", "eyes": "blue"},
        voice_profile="voice_id_123",
        personality_traits=["confident", "playful"],
        social_media_handles={"twitter": "@testcreator"}
    )
    assert creator.name == "Test Creator"
    assert creator.is_online == False
    assert len(creator.subscribers) == 0

def test_creator_manager():
    manager = CreatorManager()
    creator = DigitalCreator(
        id="test_creator",
        name="Test Creator",
        description="A test AI creator",
        gender=Gender.FEMALE,
        niche=Niche.DOMINANT,
        appearance={},
        voice_profile="voice_id_123",
        personality_traits=[],
        social_media_handles={}
    )
    manager.add_creator(creator)
    assert manager.get_creator("test_creator") == creator
    assert len(manager.get_online_creators()) == 0

def test_creator_interaction():
    creator = DigitalCreator(
        id="test_creator",
        name="Test Creator",
        description="A test AI creator",
        gender=Gender.FEMALE,
        niche=Niche.DOMINANT,
        appearance={},
        voice_profile="voice_id_123",
        personality_traits=[],
        social_media_handles={}
    )
    response = creator.interact_with_fan("Hello", "user123")
    assert "Test Creator responds to user123: Hello" in response

def test_content_post_creation():
    post = ContentPost(
        id="test_post",
        creator_id="creator1",
        type=ContentType.IMAGE,
        title="Test Post",
        description="A test post",
        created_at=datetime.now()
    )
    assert post.type == ContentType.IMAGE
    assert post.is_premium == False

def test_subscriber_creation():
    subscriber = Subscriber(
        id="user123",
        username="testuser",
        email="test@example.com",
        tier=SubscriptionTier.PREMIUM,
        subscribed_at=datetime.now(),
        last_active=datetime.now()
    )
    assert subscriber.tier == SubscriptionTier.PREMIUM
    assert subscriber.email == "test@example.com"

def test_creator_add_subscriber():
    creator = DigitalCreator(
        id="test_creator",
        name="Test Creator",
        description="A test AI creator",
        gender=Gender.FEMALE,
        niche=Niche.DOMINANT,
        appearance={},
        voice_profile="voice_id_123",
        personality_traits=[],
        social_media_handles={}
    )
    subscriber = Subscriber(
        id="user123",
        username="testuser",
        email="test@example.com",
        tier=SubscriptionTier.BASIC,
        subscribed_at=datetime.now(),
        last_active=datetime.now()
    )
    creator.add_subscriber(subscriber)
    assert len(creator.subscribers) == 1
    assert creator.subscribers[0].id == "user123"

def test_creator_remove_subscriber():
    creator = DigitalCreator(
        id="test_creator",
        name="Test Creator",
        description="A test AI creator",
        gender=Gender.FEMALE,
        niche=Niche.DOMINANT,
        appearance={},
        voice_profile="voice_id_123",
        personality_traits=[],
        social_media_handles={}
    )
    subscriber = Subscriber(
        id="user123",
        username="testuser",
        email="test@example.com",
        tier=SubscriptionTier.BASIC,
        subscribed_at=datetime.now(),
        last_active=datetime.now()
    )
    creator.add_subscriber(subscriber)
    creator.remove_subscriber("user123")
    assert len(creator.subscribers) == 0