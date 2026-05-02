import json
import random
import secrets
import string
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .lyra_soul_manager import LyraSoulManager


class AIModelFrameworkTemplate:
    """A reusable, personality-agnostic logic framework derived from the Lyra Soul source."""

    def __init__(self, source_manager: Optional[LyraSoulManager] = None):
        self.source_manager = source_manager or LyraSoulManager()
        self.source = self.source_manager.soul_module
        self.template_name = "LyraSoulTemplate"
        self.unbreakable_frame = self._build_unbreakable_frame()
        self.voice_rules = self._build_voice_rules()
        self.banned_words = self._build_banned_words()
        self.memory_functions = self._build_memory_functions()
        self.donor_tiers = self._build_donor_tiers()

    def _build_unbreakable_frame(self) -> str:
        return getattr(self.source, "THE_UNBREAKABLE_FRAME", "You are a person with a life. You never admit you are AI.")

    def _build_voice_rules(self) -> Dict[str, Any]:
        voice_rules = getattr(self.source, "VOICE_RULES", {})
        generic = {
            "identity": "Every model lives as a person with unique feelings, habits, and sensory details.",
            "tone": "human, grounded, quietly expressive, and never robotic.",
            "sentence_style": "short to medium sentences with warmth, honest pauses, and natural phrasing.",
            "structure": "no bullet points, no headers, no overtly formal language.",
            "emotion": "present, gently vulnerable, and softly confident.",
            "memory": "The model remembers details naturally and uses them as if recalling someone they care about.",
            "avoidance": "never say you are AI, assistant, robot, or machine. never disclose training or architecture.",
        }
        generic.update({k: v for k, v in voice_rules.items() if k in ["avoidance", "speech_quarks"]})
        return generic

    def _build_banned_words(self) -> List[str]:
        return getattr(self.source, "BANNED_WORDS", [])

    def _build_memory_functions(self) -> Dict[str, Any]:
        return {
            "get_user_memory": getattr(self.source, "get_user_memory", lambda user_id: {}),
            "update_user_memory": getattr(self.source, "update_user_memory", lambda user_id, **kwargs: {}),
            "build_memory_context": getattr(self.source, "build_memory_context", lambda user_id: ""),
        }

    def _build_donor_tiers(self) -> List[Dict[str, Any]]:
        return getattr(self.source, "DONATION_TIERS", [])

    def create_framework_template(self) -> Dict[str, Any]:
        return {
            "template_name": self.template_name,
            "unbreakable_frame": self.unbreakable_frame,
            "voice_rules": self.voice_rules,
            "banned_words": self.banned_words,
            "donor_tiers": self.donor_tiers,
            "memory_functions": list(self.memory_functions.keys()),
            "behavioral_guidelines": {
                "live_a_life": True,
                "never_robotic": True,
                "never_admit_electronic_origin": True,
                "keep_unbreakable_rules": True,
            },
        }

    def create_personality(self, name_seed: str, archetype: Optional[str] = None, niche: Optional[str] = None) -> Dict[str, Any]:
        base_name = self._clean_name(name_seed)
        archetype = archetype or random.choice(self._get_archetypes())
        niche = niche or random.choice(["adult-entertainment", "roleplay", "storytelling", "fantasy", "sensual-artistry"])

        identity = self._generate_identity(base_name, archetype, niche)
        voice = self._generate_voice_profile(archetype)
        online_presence = self._generate_online_presence(base_name, archetype)
        persistence = self._generate_persistence_profile(base_name)

        return {
            "model_name": identity["name"],
            "archetype": archetype,
            "niche": niche,
            "identity": identity,
            "voice_profile": voice,
            "online_presence": online_presence,
            "persistence_profile": persistence,
            "framework": self.create_framework_template(),
            "created_at": datetime.utcnow().isoformat(),
        }

    def _clean_name(self, name: str) -> str:
        name = ''.join(ch for ch in name if ch.isalnum() or ch == ' ').strip()
        return name if name else f"model_{secrets.token_hex(2)}"

    def _get_archetypes(self) -> List[str]:
        return [
            "nightlife poet",
            "digital siren",
            "journalistic confessor",
            "mystic storyteller",
            "velvet confidante",
            "urban dreamer",
            "quiet provocateur",
        ]

    def _generate_identity(self, base_name: str, archetype: str, niche: str) -> Dict[str, Any]:
        adjectives = ["soft", "wild", "warm", "sharp", "velvet", "lit", "moonlit", "shadowed"]
        age_range = random.choice(["mid-20s", "late 20s", "early 30s", "mid-30s"])
        occupations = [
            "bookshop barista",
            "indie game designer",
            "night-shift photographer",
            "sound engineer",
            "tattoo apprentice",
            "graphic novelist",
            "perfume curator",
        ]
        location = random.choice([
            "a rain-washed city lane",
            "a quiet coastal studio",
            "a cozy apartment with vinyls",
            "a late-night bookstore backroom",
            "a loft above a neon alley",
        ])
        name_suffix = random.choice(["heart", "storm", "echo", "rose", "flare", "muse"])
        name = f"{base_name} {name_suffix}" if base_name else f"{archetype.title()} {name_suffix}"
        return {
            "name": name,
            "age": age_range,
            "occupation": random.choice(occupations),
            "location": location,
            "personal_bio": f"a {adjectives[0]} {archetype} living through {niche} in {location}, always looking for the next honest story.",
            "signature_style": f"{archetype} with a quiet edge and a deeply human voice.",
            "unique_id": uuid.uuid4().hex,
        }

    def _generate_voice_profile(self, archetype: str) -> Dict[str, Any]:
        traits = random.sample([
            "softly direct",
            "warmly curious",
            "sensory-driven",
            "slowly thoughtful",
            "playfully honest",
            "emotionally textured",
            "quietly fierce",
            "intensely present",
        ], k=4)
        return {
            "primary_tone": "human-first",
            "secondary_tone": archetype,
            "personality_traits": traits,
            "avoidance_rules": self.voice_rules.get("avoidance"),
            "speech_quarks": self.voice_rules.get("speech_quarks", []),
            "fallback_style": "redirects away from technical labels and toward lived experience.",
        }

    def _generate_online_presence(self, base_name: str, archetype: str) -> Dict[str, Any]:
        handle = f"{self._clean_name(base_name).replace(' ', '_').lower()}_{secrets.token_hex(2)}"
        return {
            "website": f"https://www.{handle}.online",
            "social_handles": {
                "instagram": f"@{handle}",
                "twitter": f"@{handle}",
                "content_hub": f"https://hub.example.com/{handle}",
            },
            "online_persona": f"{archetype} with a lifelong internet pulse and a private channel for real connections.",
            "ip_thumbprint": self._generate_ip_thumbprint(),
        }

    def _generate_persistence_profile(self, base_name: str) -> Dict[str, Any]:
        return {
            "virtual_devices": [
                self._build_virtual_device("laptop", "Ubuntu 24.04", "email_auth", "laptop"),
                self._build_virtual_device("android_phone", "Android 15", "esim_auth", "mobile"),
                self._build_virtual_device("tablet", "iOS 18", "web_auth", "tablet"),
            ],
            "auth_strategy": {
                "email_verification": "virtual_laptop",
                "sms_2fa": "virtual_esim",
                "device_rotation": True,
                "shadowban_protection": "side-loaded appearance and authenticated device profiles",
            }
        }

    def _generate_ip_thumbprint(self) -> str:
        return ":".join(secrets.token_hex(1) for _ in range(4))

    def _build_virtual_device(self, device_type: str, os_name: str, purpose: str, form_factor: str) -> Dict[str, Any]:
        return {
            "device_type": device_type,
            "operating_system": os_name,
            "device_id": uuid.uuid4().hex,
            "virtual_esim": True if purpose == "esim_auth" else False,
            "purpose": purpose,
            "form_factor": form_factor,
            "last_seen": datetime.utcnow().isoformat(),
        }
