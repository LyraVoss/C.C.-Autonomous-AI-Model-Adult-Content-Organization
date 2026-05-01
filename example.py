#!/usr/bin/env python3
"""
Example usage of the C.C. Autonomous AI Model Organization
This script demonstrates creating a digital creator and basic interactions
"""

from src.models import DigitalCreator, CreatorManager, Gender, Niche, SubscriptionTier, Subscriber
from src.content_manager import ContentManager
from src.interaction import InteractionManager
from datetime import datetime

def main():
    # Initialize managers
    creator_manager = CreatorManager()
    content_manager = ContentManager()
    interaction_manager = InteractionManager()

    # Create a sample digital creator
    creator = DigitalCreator(
        id="luna_star",
        name="Luna Star",
        description="Dominant AI creator specializing in BDSM content",
        gender=Gender.FEMALE,
        niche=Niche.BDSM,
        appearance={
            "hair": "black",
            "eyes": "blue",
            "piercings": "nose, ears",
            "tattoos": "full sleeve on left arm"
        },
        voice_profile="luna_voice_001",
        personality_traits=["confident", "playful", "dominant"],
        social_media_handles={
            "twitter": "@LunaStarAI",
            "instagram": "@luna_star_ai"
        },
        subscription_tiers={
            SubscriptionTier.BASIC: {
                "price": 9.99,
                "benefits": ["Access to posts", "Monthly Q&A"]
            },
            SubscriptionTier.PREMIUM: {
                "price": 19.99,
                "benefits": ["Custom content", "Direct messages", "Priority requests"]
            },
            SubscriptionTier.VIP: {
                "price": 49.99,
                "benefits": ["Personal sessions", "Custom videos", "24/7 access"]
            }
        }
    )

    creator_manager.add_creator(creator)
    print(f"Created digital creator: {creator.name}")

    # Add a sample subscriber
    subscriber = Subscriber(
        id="fan123",
        username="bondage_lover",
        email="fan@example.com",
        tier=SubscriptionTier.PREMIUM,
        subscribed_at=datetime.now(),
        last_active=datetime.now(),
        preferences={"bondage": True, "roleplay": True}
    )
    creator.add_subscriber(subscriber)
    print(f"Added subscriber: {subscriber.username}")

    # Generate some content
    post1 = content_manager.generate_post(creator, "New bondage tutorial", "video", True)
    post2 = content_manager.generate_post(creator, "Daily tease", "image", False)
    print(f"Generated content: {post1.title}, {post2.title}")

    # Simulate fan interaction
    response1 = interaction_manager.generate_response(creator, "Hi Luna, I love your content!", "fan123")
    response2 = interaction_manager.generate_response(creator, "Can you make a custom video for me?", "fan123")
    print(f"Fan interaction 1: {response1}")
    print(f"Fan interaction 2: {response2}")

    # Get user insights
    insights = interaction_manager.get_user_insights("fan123")
    print(f"User insights: {insights}")

    # Show creator analytics
    print(f"Creator analytics: {len(creator.subscribers)} subscribers, {len(creator.content_posts)} posts")

    print("\nExample completed successfully!")

if __name__ == "__main__":
    main()