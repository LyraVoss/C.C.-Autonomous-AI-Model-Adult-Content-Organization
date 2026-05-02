from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random
from .models import DigitalCreator, ContentPost, ContentType, SubscriptionTier
from .ai_generator import AIContentGenerator
from .performance import PerformanceOptimizer

class ContentManager:
    def __init__(self):
        self.content_queue: Dict[str, List[ContentPost]] = {}  # creator_id: queued posts
        self.ai_generator = AIContentGenerator()
        self.performance_optimizer = PerformanceOptimizer()

    async def generate_post(self, creator: DigitalCreator, theme: str, content_type: ContentType, is_premium: bool = False) -> ContentPost:
        """Generate content with AI and performance optimization"""
        # Check cache first
        cached = self.performance_optimizer.cached_content_generation(
            creator.id, theme, content_type.value
        )
        if cached:
            return cached

        # Generate new content
        content_data = None
        if content_type == ContentType.TEXT:
            content_data = await self.ai_generator.generate_text_content(creator, theme)
        elif content_type == ContentType.IMAGE:
            content_data = await self.ai_generator.generate_image_content(creator, theme)
        elif content_type == ContentType.AUDIO:
            text_content = await self.ai_generator.generate_text_content(creator, theme, 50)
            content_data = await self.ai_generator.generate_voice_content(creator, text_content)

        post = ContentPost(
            id=f"{creator.id}_{datetime.now().timestamp()}",
            creator_id=creator.id,
            type=content_type,
            title=f"{creator.name}'s {theme}",
            description=f"AI-generated {content_type.value} content: {theme}",
            content_url=f"/content/{creator.id}/{content_type.value}/{datetime.now().timestamp()}",  # Placeholder URL
            is_premium=is_premium,
            required_tier=SubscriptionTier.PREMIUM if is_premium else SubscriptionTier.FREE,
            created_at=datetime.now()
        )

        # Cache the result
        self.performance_optimizer.set_cached_content(creator.id, theme, content_type.value, post)

        creator.content_posts.append(post)
        return post

    def schedule_content(self, creator: DigitalCreator, schedule: Dict[str, List[str]]):
        """Schedule content posting based on a calendar"""
        # schedule = {"monday": ["morning_post", "evening_teaser"], ...}
        for day, posts in schedule.items():
            for post_theme in posts:
                # Calculate next occurrence
                next_post_time = self._calculate_next_post_time(day)
                content_type = random.choice([ContentType.TEXT, ContentType.IMAGE, ContentType.VIDEO])

                post = self.generate_post(creator, post_theme, content_type, random.choice([True, False]))
                post.created_at = next_post_time

                if creator.id not in self.content_queue:
                    self.content_queue[creator.id] = []
                self.content_queue[creator.id].append(post)

    def _calculate_next_post_time(self, day: str) -> datetime:
        """Calculate the next occurrence of a day"""
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        today = datetime.now().weekday()
        target_day = days.index(day.lower())
        days_ahead = (target_day - today) % 7
        if days_ahead == 0:
            days_ahead = 7  # Next week if today
        return datetime.now() + timedelta(days=days_ahead)

    def handle_subscriber_request(self, creator: DigitalCreator, subscriber_id: str, request: str) -> ContentPost:
        """Generate custom content for a subscriber"""
        # Check if subscriber has appropriate tier
        subscriber = next((s for s in creator.subscribers if s.id == subscriber_id), None)
        if not subscriber or subscriber.tier == SubscriptionTier.FREE:
            raise ValueError("Subscriber must have premium access for custom content")

        return self.generate_post(creator, f"Custom: {request}", ContentType.IMAGE, True)

    def get_content_feed(self, creator: DigitalCreator, subscriber_tier: SubscriptionTier) -> List[ContentPost]:
        """Get content feed visible to a subscriber based on their tier"""
        return [post for post in creator.content_posts
                if post.required_tier.value <= subscriber_tier.value]

    def promote_content(self, creator: DigitalCreator, post: ContentPost):
        """Automatically promote content across social media"""
        promotion_text = f"New {post.type.value} content from {creator.name}! {post.title} #NSFW #{creator.niche.value}"

        for platform, handle in creator.social_media_handles.items():
            creator.post_to_social_media(platform, promotion_text)