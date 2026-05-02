import openai
import requests
from typing import Optional, Dict, Any
from PIL import Image
import io
import os
from datetime import datetime
from .models import DigitalCreator, ContentType

class AIContentGenerator:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = None
        if self.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.stability_api_key = os.getenv("STABILITY_API_KEY")  # For image generation

    async def generate_text_content(self, creator: DigitalCreator, theme: str, word_count: int = 200) -> str:
        """Generate hyper-realistic text content using GPT-4"""
        prompt = f"""You are {creator.name}, a {creator.niche.value} adult content creator with these traits: {', '.join(creator.personality_traits)}.

Appearance: {creator.appearance}
Personality: {', '.join(creator.personality_traits)}

Write a {word_count}-word erotic story about: {theme}

Make it hyper-realistic, immersive, and engaging. Use first-person perspective. Include sensory details and build tension naturally."""

        response = await self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=word_count * 2,
            temperature=0.8
        )

        return response.choices[0].message.content.strip()

    async def generate_image_content(self, creator: DigitalCreator, theme: str, style: str = "realistic") -> bytes:
        """Generate hyper-realistic images using Stable Diffusion"""
        prompt = f"""Hyper-realistic photograph of {creator.name}, {creator.appearance.get('hair', 'long hair')}, {creator.appearance.get('eyes', 'blue eyes')}, {creator.appearance.get('body', 'fit body')}, wearing {creator.appearance.get('piercings', 'minimal piercings')}, with {creator.appearance.get('tattoos', 'some tattoos')}.

{theme}. Professional studio lighting, 8k resolution, photorealistic, detailed skin texture, seductive pose, adult content."""

        # Using Stability AI API (assuming it's available)
        # In practice, you'd integrate with their API
        # For now, return placeholder
        return b"placeholder_image_data"

    async def generate_voice_content(self, creator: DigitalCreator, text: str, voice_id: Optional[str] = None) -> bytes:
        """Generate hyper-realistic voice using ElevenLabs"""
        voice_id = voice_id or creator.voice_profile

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.elevenlabs_api_key
        }

        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "style": 0.5,
                "use_speaker_boost": True
            }
        }

        response = requests.post(url, json=data, headers=headers)
        return response.content

    async def generate_video_content(self, creator: DigitalCreator, theme: str, duration: int = 30) -> bytes:
        """Generate video content (placeholder - would require advanced AI video generation)"""
        # This would integrate with tools like RunwayML, Pika Labs, etc.
        # For now, return placeholder
        return b"placeholder_video_data"

    async def enhance_content_hyper_realism(self, content: str, creator: DigitalCreator) -> str:
        """Enhance existing content for hyper-realism using AI"""
        prompt = f"""Enhance this adult content to be hyper-realistic and immersive. Add sensory details, emotional depth, and make it feel authentic to {creator.name}'s personality.

Original content: {content}

Enhanced version:"""

        response = await self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=len(content.split()) * 1.5,
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    def get_content_metadata(self, creator: DigitalCreator, content_type: ContentType, theme: str) -> Dict[str, Any]:
        """Generate metadata for content"""
        return {
            "creator_id": creator.id,
            "type": content_type.value,
            "theme": theme,
            "generated_at": datetime.utcnow(),
            "ai_models_used": ["gpt-4", "stable-diffusion", "elevenlabs"],
            "hyper_realism_score": 9.5,  # Placeholder
            "content_warnings": ["adult_content", "explicit"],
            "niche_tags": [creator.niche.value] + creator.personality_traits
        }