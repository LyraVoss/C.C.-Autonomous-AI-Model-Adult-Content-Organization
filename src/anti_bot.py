import random
import time
import re
from typing import Dict, Optional
import requests

class FreeAntiBotWorkflow:
    """A lightweight, free anti-bot workflow using randomized headers and human-like behavior."""

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/605.1"
    ]

    def __init__(self, proxies: Optional[Dict[str, str]] = None):
        self.proxies = proxies or {}

    def build_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive"
        }

    def human_delay(self, min_seconds: float = 1.0, max_seconds: float = 2.5) -> None:
        time.sleep(random.uniform(min_seconds, max_seconds))

    def generate_form_payload(self, data: Dict[str, str]) -> Dict[str, str]:
        return {k: str(v) for k, v in data.items()}

    def detect_bot_challenge(self, html: str) -> Optional[str]:
        lower = html.lower()
        if "recaptcha" in lower or "g-recaptcha" in lower:
            return "recaptcha"
        if "hcaptcha" in lower:
            return "hcaptcha"
        if "are you human" in lower or "prove you are human" in lower:
            return "text_challenge"
        return None

    def solve_text_challenge(self, html: str) -> Optional[str]:
        match = re.search(r"what is (\d+) \+ (\d+)", html.lower())
        if match:
            a, b = int(match.group(1)), int(match.group(2))
            return str(a + b)
        return None

    def post_form(self, url: str, data: Dict[str, str], additional_headers: Optional[Dict[str, str]] = None) -> Optional[requests.Response]:
        session = requests.Session()
        headers = self.build_headers()
        if additional_headers:
            headers.update(additional_headers)
        session.headers.update(headers)
        try:
            self.human_delay(2.0, 4.5)
            response = session.post(url, data=self.generate_form_payload(data), proxies=self.proxies, timeout=30)
            if response.status_code in {200, 201, 302}:
                return response
            return response
        except Exception:
            return None

    def get_page(self, url: str, additional_headers: Optional[Dict[str, str]] = None) -> Optional[requests.Response]:
        session = requests.Session()
        headers = self.build_headers()
        if additional_headers:
            headers.update(additional_headers)
        session.headers.update(headers)
        try:
            self.human_delay(1.0, 3.5)
            response = session.get(url, proxies=self.proxies, timeout=30)
            return response
        except Exception:
            return None
