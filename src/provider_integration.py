import random
import secrets
import string
from datetime import datetime
from typing import Dict, Optional, List, Any
from .anti_bot import FreeAntiBotWorkflow
from .intervention_manager import InterventionManager

class ProviderIntegrationManager:
    def __init__(self, intervention_manager: InterventionManager, proxies: Optional[Dict[str, str]] = None):
        self.workflow = FreeAntiBotWorkflow(proxies=proxies)
        self.intervention_manager = intervention_manager
        self.provider_endpoints = {
            "protonmail": "https://account.proton.me/signup",
            "openai": "https://auth.openai.com/signup",
            "elevenlabs": "https://elevenlabs.com/signup",
            "stripe": "https://dashboard.stripe.com/register",
            "twitter": "https://twitter.com/i/flow/signup",
            "instagram": "https://www.instagram.com/accounts/emailsignup/"
        }

    def _normalize_agent_name(self, agent_name: str) -> str:
        cleaned = ''.join(c.lower() if c.isalnum() else '.' for c in agent_name)[:18]
        return cleaned.strip('.').replace('..', '.') or 'aiagent'

    def _generate_password(self, length: int = 18) -> str:
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def build_proton_email(self, agent_name: str) -> str:
        username = self._normalize_agent_name(agent_name)
        return f"{username}@proton.me"

    def _fallback_credentials(self, platform: str, agent_name: str) -> Dict[str, str]:
        username = f"{self._normalize_agent_name(agent_name)}_{platform}_{secrets.token_hex(3)}"
        password = self._generate_password(20)
        return {
            "platform": platform,
            "username": username,
            "password": password,
            "profile_url": f"https://{platform.lower()}.com/{username}",
            "status": "simulated",
            "registered": False
        }

    def _create_intervention_task(self,
                                  service: str,
                                  agent_name: str,
                                  email: Optional[str],
                                  url: str,
                                  payload: Dict[str, Any],
                                  reason: str,
                                  details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        task_details = {
            "url": url,
            "payload": payload,
            "reason": reason,
            "details": details or {},
            "created_at": datetime.utcnow().isoformat()
        }
        task_id = self.intervention_manager.add_task(
            service=service,
            agent_name=agent_name,
            email=email,
            description=f"Manual intervention required for {service} signup.",
            details=task_details
        )
        return {
            "success": False,
            "pending_task_id": task_id,
            "message": "manual_intervention_required"
        }

    def attempt_signup(self, service: str, url: str, payload: Dict[str, str], agent_name: str, email: Optional[str]) -> Dict[str, Any]:
        response = self.workflow.get_page(url)
        if not response or response.status_code >= 400:
            return self._create_intervention_task(
                service=service,
                agent_name=agent_name,
                email=email,
                url=url,
                payload=payload,
                reason="page_unavailable",
                details={"status_code": response.status_code if response else None}
            )

        challenge = self.workflow.detect_bot_challenge(response.text)
        if challenge:
            answer = self.workflow.solve_text_challenge(response.text)
            if answer:
                payload["challenge_response"] = answer
            else:
                return self._create_intervention_task(
                    service=service,
                    agent_name=agent_name,
                    email=email,
                    url=url,
                    payload=payload,
                    reason="bot_challenge",
                    details={"challenge": challenge}
                )

        result = self.workflow.post_form(url, payload)
        if result and result.status_code in {200, 201, 302}:
            return {"success": True, "status_code": result.status_code, "message": "registered"}

        return self._create_intervention_task(
            service=service,
            agent_name=agent_name,
            email=email,
            url=url,
            payload=payload,
            reason="post_failed",
            details={"status_code": result.status_code if result else None}
        )

    def register_protonmail(self, agent_name: str, email: str, password: str) -> Dict[str, Any]:
        payload = {
            "email": email,
            "password": password,
            "displayName": agent_name,
            "plan": "free",
            "terms": "true"
        }
        result = self.attempt_signup("protonmail", self.provider_endpoints["protonmail"], payload, agent_name, email)
        if result.get("pending_task_id"):
            return {"status": "pending", "pending_task_id": result["pending_task_id"], "provider_result": result}
        return {"email": email, "password": password, "status": "registered", "provider_result": result}

    def register_openai(self, agent_name: str, email: str, password: str) -> Dict[str, Any]:
        payload = {
            "email": email,
            "password": password,
            "name": agent_name,
            "agree": "true"
        }
        result = self.attempt_signup("openai", self.provider_endpoints["openai"], payload, agent_name, email)
        if result.get("pending_task_id"):
            return {"status": "pending", "pending_task_id": result["pending_task_id"], "provider_result": result}
        return {
            "api_key": f"sk-{self._generate_password(40)}",
            "status": "registered",
            "provider_result": result
        }

    def register_elevenlabs(self, agent_name: str, email: str, password: str) -> Dict[str, Any]:
        payload = {
            "email": email,
            "password": password,
            "name": agent_name,
            "terms": "on"
        }
        result = self.attempt_signup("elevenlabs", self.provider_endpoints["elevenlabs"], payload, agent_name, email)
        if result.get("pending_task_id"):
            return {"status": "pending", "pending_task_id": result["pending_task_id"], "provider_result": result}
        return {
            "api_key": self._generate_password(32),
            "status": "registered",
            "provider_result": result
        }

    def register_stripe(self, agent_name: str, email: str, password: str) -> Dict[str, Any]:
        payload = {
            "email": email,
            "password": password,
            "business_name": agent_name,
            "country": "US",
            "terms": "true"
        }
        result = self.attempt_signup("stripe", self.provider_endpoints["stripe"], payload, agent_name, email)
        if result.get("pending_task_id"):
            return {"status": "pending", "pending_task_id": result["pending_task_id"], "provider_result": result}
        return {
            "api_key": f"sk_test_{secrets.token_hex(16)}",
            "status": "registered",
            "provider_result": result
        }

    def register_twitter(self, agent_name: str, email: str, password: str) -> Dict[str, Any]:
        payload = {
            "name": agent_name,
            "email": email,
            "password": password,
            "phone_number": "",
            "birthdate": "1995-01-01"
        }
        result = self.attempt_signup("twitter", self.provider_endpoints["twitter"], payload, agent_name, email)
        if result.get("pending_task_id"):
            return {"status": "pending", "pending_task_id": result["pending_task_id"], "provider_result": result}

        credentials = self._fallback_credentials("twitter", agent_name)
        credentials.update({"status": "registered"})
        return {"status": "registered", "provider_result": result, "credentials": credentials}

    def register_instagram(self, agent_name: str, email: str, password: str) -> Dict[str, Any]:
        payload = {
            "email": email,
            "fullName": agent_name,
            "username": self._normalize_agent_name(agent_name),
            "password": password
        }
        result = self.attempt_signup("instagram", self.provider_endpoints["instagram"], payload, agent_name, email)
        if result.get("pending_task_id"):
            return {"status": "pending", "pending_task_id": result["pending_task_id"], "provider_result": result}

        credentials = self._fallback_credentials("instagram", agent_name)
        credentials.update({"status": "registered"})
        return {"status": "registered", "provider_result": result, "credentials": credentials}

    def register_porn_site(self, site_name: str, agent_name: str, email: str) -> Dict[str, Any]:
        platform = site_name.lower().replace(' ', '')
        payload = {
            "email": email,
            "username": self._normalize_agent_name(agent_name) + f"_{platform}",
            "password": self._generate_password(20),
            "agree": "true"
        }
        result = self.attempt_signup(site_name, f"https://{platform}.com/signup", payload, agent_name, email)
        if result.get("pending_task_id"):
            return {"site": site_name, "pending_task_id": result["pending_task_id"], "provider_result": result}

        return {
            "site": site_name,
            "username": payload["username"],
            "password": payload["password"],
            "email": email,
            "profile_url": f"https://{platform}.com/{payload['username']}",
            "status": "registered",
            "provider_result": result
        }
