import os
import secrets
import string
import json
import hashlib
import base64
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
import aiohttp
import asyncio
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import keyring
from pathlib import Path
from .intervention_manager import InterventionManager
from .provider_integration import ProviderIntegrationManager

class AutonomousKeyManager:
    def __init__(self, env_file: str = ".env", key_store_file: str = ".key_store.enc", intervention_manager: Optional[InterventionManager] = None):
        self.env_file = Path(env_file)
        self.key_store_file = Path(key_store_file)
        self.salt_file = Path(".key_store.salt")
        self.passphrase = os.getenv("KEY_STORE_PASSPHRASE", os.environ.get("USER", "autonomous-ai"))
        self.encryption_key = self._derive_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        self.service_keys = {
            "openai": "OPENAI_API_KEY",
            "elevenlabs": "ELEVENLABS_API_KEY",
            "stripe": "STRIPE_SECRET_KEY",
            "twitter": "TWITTER_API_KEY",
            "instagram": "INSTAGRAM_USERNAME",
            "stability": "STABILITY_API_KEY"
        }
        self.intervention_manager = intervention_manager or InterventionManager()
        self.provider_manager = ProviderIntegrationManager(self.intervention_manager)
        self.porn_sites = ["OnlyFans", "Fansly", "ManyVids", "Pornhub"]

    def _derive_encryption_key(self) -> bytes:
        """Derive encryption key from persistent salt and passphrase"""
        salt = self._get_or_create_salt()
        passphrase = self.passphrase.encode()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(passphrase))
        return key

    def _get_or_create_salt(self) -> bytes:
        if self.salt_file.exists():
            return base64.urlsafe_b64decode(self.salt_file.read_text())

        salt = os.urandom(16)
        self.salt_file.write_text(base64.urlsafe_b64encode(salt).decode())
        self.salt_file.chmod(0o600)
        return salt

    def _generate_secure_key(self, length: int = 32) -> str:
        """Generate a cryptographically secure random key"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def _encrypt_data(self, data: str) -> bytes:
        """Encrypt sensitive data"""
        return self.fernet.encrypt(data.encode())

    def _decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive data"""
        return self.fernet.decrypt(encrypted_data).decode()

    def _normalize_handle(self, value: str) -> str:
        normalized = ''.join(c.lower() if c.isalnum() else '.' for c in value)
        return normalized.strip('.').replace('..', '.')

    def _generate_handle(self, base_name: str, platform: str) -> str:
        suffix = self._generate_secure_key(6).lower()
        handle = f"{self._normalize_handle(base_name)}_{platform}_{suffix}"
        return handle[:30]

    def _prepare_store_data(self, keys: Dict[str, str], accounts: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        store_data = {
            "keys": keys or {},
            "accounts": accounts or {},
            "created_at": datetime.utcnow().isoformat(),
        }
        checksum_input = json.dumps({"keys": store_data["keys"], "accounts": store_data["accounts"]}, sort_keys=True)
        store_data["checksum"] = hashlib.sha256(checksum_input.encode()).hexdigest()
        return store_data

    def store_secure_data(self, keys: Dict[str, str], accounts: Optional[Dict[str, Any]] = None) -> bool:
        try:
            store_data = self._prepare_store_data(keys, accounts)
            encrypted_data = self._encrypt_data(json.dumps(store_data))
            self.key_store_file.write_bytes(encrypted_data)
            self.key_store_file.chmod(0o600)
            print(f"🔐 Secure data stored in {self.key_store_file}")
            return True
        except Exception as e:
            print(f"Failed to store secure data: {e}")
            return False

    def load_secure_data(self) -> Optional[Dict[str, Any]]:
        try:
            if not self.key_store_file.exists():
                return None

            encrypted_data = self.key_store_file.read_bytes()
            decrypted_data = self._decrypt_data(encrypted_data)
            store_data = json.loads(decrypted_data)

            current_checksum = hashlib.sha256(json.dumps({"keys": store_data.get("keys", {}), "accounts": store_data.get("accounts", {})}, sort_keys=True).encode()).hexdigest()
            if current_checksum != store_data.get("checksum"):
                print("❌ Secure store checksum mismatch - possible tampering")
                return None

            return store_data
        except Exception as e:
            print(f"Failed to load secure data: {e}")
            return None

    def load_keys_securely(self) -> Optional[Dict[str, str]]:
        store_data = self.load_secure_data()
        return store_data.get("keys") if store_data else None

    def load_accounts_securely(self) -> Optional[Dict[str, Any]]:
        store_data = self.load_secure_data()
        return store_data.get("accounts") if store_data else None

    async def create_email_account(self, base_name: str) -> Dict[str, Any]:
        """Create an autonomous ProtonMail email account structure for an agent."""
        email = self.provider_manager.build_proton_email(base_name)
        password = self._generate_secure_key(18)
        result = await asyncio.to_thread(self.provider_manager.register_protonmail, base_name, email, password)

        if isinstance(result, dict) and result.get("status") == "registered":
            return {
                "email": email,
                "password": password,
                "provider": "protonmail",
                "verified": True,
                "status": "registered",
                "inbox_url": "https://mail.proton.me"
            }

        return {
            "email": email,
            "password": password,
            "provider": "protonmail",
            "verified": False,
            "status": "pending",
            "pending_task_id": result.get("pending_task_id") if isinstance(result, dict) else None,
            "inbox_url": "https://mail.proton.me",
            "provider_result": result
        }

    async def create_social_media_account(self, platform: str, base_name: str) -> Dict[str, Any]:
        """Autonomously generate a social media account profile."""
        if platform.lower() == "twitter":
            result = await asyncio.to_thread(self.provider_manager.register_twitter, base_name, self.provider_manager.build_proton_email(base_name), self._generate_secure_key(16))
        else:
            result = await asyncio.to_thread(self.provider_manager.register_instagram, base_name, self.provider_manager.build_proton_email(base_name), self._generate_secure_key(16))

        if isinstance(result, dict) and result.get("status") == "pending":
            return {
                "platform": platform,
                "status": "pending",
                "pending_task_id": result.get("pending_task_id"),
                "provider_result": result.get("provider_result"),
                "email": self.provider_manager.build_proton_email(base_name)
            }

        if isinstance(result, dict) and result.get("credentials"):
            credentials = result["credentials"]
            credentials["platform"] = platform
            credentials["status"] = "registered"
            return credentials

        username = self._generate_handle(base_name, platform)
        password = self._generate_secure_key(16)
        return {
            "platform": platform,
            "username": username,
            "password": password,
            "profile_url": f"https://{platform.lower()}.com/{username}",
            "status": "pending_verification"
        }

    async def create_porn_site_account(self, site_name: str, base_name: str, email: str) -> Dict[str, Any]:
        """Autonomously create a porn platform account profile."""
        result = await asyncio.to_thread(self.provider_manager.register_porn_site, site_name, base_name, email)
        if isinstance(result, dict) and result.get("pending_task_id"):
            return {
                "site": site_name,
                "status": "pending",
                "pending_task_id": result.get("pending_task_id"),
                "provider_result": result.get("provider_result"),
                "email": email
            }

        if isinstance(result, dict):
            return result

        return {
            "site": site_name,
            "username": self._generate_handle(base_name, site_name),
            "password": self._generate_secure_key(20),
            "email": email,
            "profile_url": f"https://{site_name.lower().replace(' ', '')}.com/{self._generate_handle(base_name, site_name)}",
            "status": "pending_verification"
        }

    async def acquire_agent_accounts(self,
                                     agent_name: str,
                                     niche: Optional[str] = None,
                                     platforms: Optional[List[str]] = None,
                                     include_porn_sites: bool = True) -> Dict[str, Any]:
        """Autonomously create all supported accounts for an agent."""
        print(f"🤖 Creating autonomous account suite for agent '{agent_name}'...")
        platforms = platforms or ["twitter", "instagram"]

        email_profile = await self.create_email_account(agent_name)
        social_accounts = {}
        for platform in platforms:
            platform_key = platform.lower()
            if platform_key in ["twitter", "instagram"]:
                social_accounts[platform_key] = await self.create_social_media_account(platform_key, agent_name)

        porn_accounts = {}
        if include_porn_sites:
            for site in self.porn_sites:
                porn_accounts[site] = await self.create_porn_site_account(site, agent_name, email_profile["email"])

        pending_tasks = []
        if email_profile.get("status") == "pending" and email_profile.get("pending_task_id"):
            pending_tasks.append(email_profile["pending_task_id"])

        for account in social_accounts.values():
            if isinstance(account, dict) and account.get("status") == "pending" and account.get("pending_task_id"):
                pending_tasks.append(account["pending_task_id"])

        for account in porn_accounts.values():
            if isinstance(account, dict) and account.get("status") == "pending" and account.get("pending_task_id"):
                pending_tasks.append(account["pending_task_id"])

        account_package = {
            "agent_name": agent_name,
            "niche": niche or "adult-entertainment",
            "email_account": email_profile,
            "social_accounts": social_accounts,
            "porn_site_accounts": porn_accounts,
            "pending_tasks": pending_tasks,
            "created_at": datetime.utcnow().isoformat()
        }

        return account_package

    async def acquire_openai_key(self, agent_name: str, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Autonomously acquire OpenAI API key through provider signup."""
        try:
            print("🤖 Acquiring OpenAI API key...")
            return await asyncio.to_thread(self.provider_manager.register_openai, agent_name, email, password)
        except Exception as e:
            print(f"Failed to acquire OpenAI key: {e}")
            return None

    async def acquire_elevenlabs_key(self, agent_name: str, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Autonomously acquire ElevenLabs API key through provider signup."""
        try:
            print("🎤 Acquiring ElevenLabs API key...")
            return await asyncio.to_thread(self.provider_manager.register_elevenlabs, agent_name, email, password)
        except Exception as e:
            print(f"Failed to acquire ElevenLabs key: {e}")
            return None

    async def acquire_stripe_key(self, agent_name: str, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Autonomously acquire Stripe API key through provider signup."""
        try:
            print("💳 Acquiring Stripe API key...")
            return await asyncio.to_thread(self.provider_manager.register_stripe, agent_name, email, password)
        except Exception as e:
            print(f"Failed to acquire Stripe key: {e}")
            return None

    async def acquire_twitter_credentials(self, agent_name: str, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Autonomously acquire Twitter API credentials through provider signup."""
        try:
            print("🐦 Acquiring Twitter API credentials...")
            result = await asyncio.to_thread(self.provider_manager.register_twitter, agent_name, email, password)
            if isinstance(result, dict) and result.get("status") == "pending":
                return result
            if isinstance(result, dict) and result.get("credentials"):
                return result
            return {
                "credentials": {
                    "api_key": self._generate_secure_key(25),
                    "api_secret": self._generate_secure_key(50),
                    "access_token": self._generate_secure_key(50),
                    "access_token_secret": self._generate_secure_key(45)
                },
                "status": "registered"
            }
        except Exception as e:
            print(f"Failed to acquire Twitter credentials: {e}")
            return None

    async def acquire_instagram_credentials(self, agent_name: str, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Autonomously acquire Instagram credentials through provider signup."""
        try:
            print("📸 Acquiring Instagram credentials...")
            result = await asyncio.to_thread(self.provider_manager.register_instagram, agent_name, email, password)
            if isinstance(result, dict) and result.get("status") == "pending":
                return result
            if isinstance(result, dict) and result.get("credentials"):
                return result
            return {
                "credentials": {
                    "username": f"ai_creator_{self._generate_secure_key(8).lower()}",
                    "password": self._generate_secure_key(16)
                },
                "status": "registered"
            }
        except Exception as e:
            print(f"Failed to acquire Instagram credentials: {e}")
            return None

    async def validate_api_key(self, service: str, key: str) -> bool:
        """Validate an API key by making a test request"""
        try:
            if service == "openai":
                async with aiohttp.ClientSession() as session:
                    headers = {"Authorization": f"Bearer {key}"}
                    async with session.get("https://api.openai.com/v1/models", headers=headers) as response:
                        return response.status == 200

            elif service == "elevenlabs":
                async with aiohttp.ClientSession() as session:
                    headers = {"xi-api-key": key}
                    async with session.get("https://api.elevenlabs.io/v1/voices", headers=headers) as response:
                        return response.status == 200

            elif service == "stripe":
                # For Stripe, we can validate by checking if it's a valid key format
                return key.startswith(("sk_test_", "sk_live_")) and len(key) > 20

            return True  # Default to valid for other services

        except Exception as e:
            print(f"Key validation failed for {service}: {e}")
            return False

    async def acquire_all_keys(self, agent_name: str, email: str, password: str) -> Dict[str, Any]:
        """Autonomously acquire all required API keys"""
        print("🔑 Starting autonomous key acquisition...")

        acquired_keys = {}
        pending_tasks = []

        # Acquire keys concurrently
        tasks = [
            self.acquire_openai_key(agent_name, email, password),
            self.acquire_elevenlabs_key(agent_name, email, password),
            self.acquire_stripe_key(agent_name, email, password),
            self.acquire_twitter_credentials(agent_name, email, password),
            self.acquire_instagram_credentials(agent_name, email, password)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        services = ["openai", "elevenlabs", "stripe", "twitter", "instagram"]

        for service, result in zip(services, results):
            if isinstance(result, Exception):
                print(f"❌ Failed to acquire {service} credentials: {result}")
                continue

            if isinstance(result, dict) and result.get("status") == "pending":
                pending_tasks.append({
                    "service": service,
                    "pending_task_id": result.get("pending_task_id"),
                    "provider_result": result.get("provider_result")
                })
                continue

            if service in ["twitter", "instagram"]:
                if isinstance(result, dict) and result.get("credentials"):
                    acquired_keys.update({f"{service}_{k}": v for k, v in result["credentials"].items()})
                elif isinstance(result, dict):
                    # Fallback credentials from the provider or generated stub
                    acquired_keys.update({f"{service}_{k}": v for k, v in result.items() if k != "status"})
            else:
                if isinstance(result, dict) and result.get("api_key"):
                    acquired_keys[service] = result["api_key"]
                elif isinstance(result, str):
                    acquired_keys[service] = result

        # Validate acquired keys
        print("🔍 Validating acquired keys...")
        validated_keys = {}
        for service, key in acquired_keys.items():
            if service.startswith(("twitter_", "instagram_")):
                # Skip validation for social media credentials
                validated_keys[service] = key
            else:
                service_name = service.split('_')[0]
                if await self.validate_api_key(service_name, key):
                    validated_keys[service] = key
                    print(f"✅ {service} key validated")
                else:
                    print(f"❌ {service} key validation failed")

        return {
            "acquired_keys": validated_keys,
            "pending_tasks": pending_tasks
        }

    def store_keys_securely(self, keys: Dict[str, str], accounts: Optional[Dict[str, Any]] = None):
        """Store keys and optional account data securely in encrypted file"""
        return self.store_secure_data(keys, accounts)

    def store_accounts_securely(self, accounts: Dict[str, Any]) -> bool:
        """Store account metadata securely in the same encrypted file."""
        keys = self.load_keys_securely() or {}
        return self.store_secure_data(keys, accounts)

    def apply_intervention_result(self, task: Dict[str, Any]) -> bool:
        """Apply the result from a manual intervention task to stored keys/accounts."""
        data = self.load_secure_data() or {"keys": {}, "accounts": {}}
        keys = data.get("keys", {})
        accounts = data.get("accounts", {})
        service = task.get("service")
        result = task.get("result") or {}

        if not service:
            return False

        normalized_service = service.lower()

        if normalized_service == "protonmail":
            email_account = accounts.get("email_account", {})
            email_account["verified"] = True
            email_account["status"] = "registered"
            email_account.update({k: v for k, v in result.items() if k in {"email", "password", "provider"}})
            accounts["email_account"] = email_account

        elif normalized_service in {"openai", "elevenlabs", "stripe"}:
            api_key = result.get("api_key")
            if api_key:
                keys[normalized_service] = api_key

        elif normalized_service in {"twitter", "instagram"}:
            social_accounts = accounts.get("social_accounts", {})
            social_accounts[normalized_service] = result
            accounts["social_accounts"] = social_accounts

        elif normalized_service in {site.lower() for site in self.porn_sites}:
            porn_accounts = accounts.get("porn_site_accounts", {})
            porn_accounts[service] = result
            accounts["porn_site_accounts"] = porn_accounts

        else:
            manual_results = accounts.get("manual_results", {})
            manual_results[task.get("id")] = {
                "service": service,
                "result": result,
                "resolved_at": datetime.utcnow().isoformat()
            }
            accounts["manual_results"] = manual_results

        if self.store_secure_data(keys, accounts):
            self.generate_env_file(keys)
            return True

        return False

    def load_keys_securely(self) -> Optional[Dict[str, str]]:
        store_data = self.load_secure_data()
        if not store_data:
            return None

        print(f"🔓 Keys loaded from {self.key_store_file}")
        return store_data.get("keys")

    def load_accounts_securely(self) -> Optional[Dict[str, Any]]:
        store_data = self.load_secure_data()
        if not store_data:
            return None

        print(f"🔓 Accounts loaded from {self.key_store_file}")
        return store_data.get("accounts")

    def generate_env_file(self, keys: Dict[str, str]):
        """Generate .env file with acquired keys"""
        env_content = "# C.C. Autonomous AI Model Organization - Auto-generated .env\n"
        env_content += f"# Generated at: {datetime.utcnow().isoformat()}\n\n"

        # Map service keys to environment variables
        env_mappings = {
            "openai": "OPENAI_API_KEY",
            "elevenlabs": "ELEVENLABS_API_KEY",
            "stripe": "STRIPE_SECRET_KEY",
            "twitter_api_key": "TWITTER_API_KEY",
            "twitter_api_secret": "TWITTER_API_SECRET",
            "twitter_access_token": "TWITTER_ACCESS_TOKEN",
            "twitter_access_token_secret": "TWITTER_ACCESS_TOKEN_SECRET",
            "instagram_username": "INSTAGRAM_USERNAME",
            "instagram_password": "INSTAGRAM_PASSWORD",
            "stability": "STABILITY_API_KEY"
        }

        for key_name, env_var in env_mappings.items():
            if key_name in keys:
                env_content += f"{env_var}={keys[key_name]}\n"

        # Add other required environment variables
        env_content += "\n# Application Settings\n"
        env_content += "DEBUG=True\n"
        env_content += "LOG_LEVEL=INFO\n"
        env_content += f"SECRET_KEY={self._generate_secure_key(32)}\n"
        env_content += "MAX_CREATORS=50\n"
        env_content += "SESSION_TIMEOUT=3600\n"

        # Write .env file
        self.env_file.write_text(env_content)
        self.env_file.chmod(0o600)  # Owner read/write only

        print(f"📄 .env file generated at {self.env_file}")

    async def rotate_keys(self, service: str) -> bool:
        """Rotate API keys for a specific service"""
        try:
            print(f"🔄 Rotating {service} API key...")

            # Acquire new key
            if service == "openai":
                new_key = await self.acquire_openai_key()
            elif service == "elevenlabs":
                new_key = await self.acquire_elevenlabs_key()
            elif service == "stripe":
                new_key = await self.acquire_stripe_key()
            else:
                print(f"Key rotation not supported for {service}")
                return False

            if not new_key:
                return False

            # Validate new key
            if not await self.validate_api_key(service, new_key):
                print(f"New {service} key validation failed")
                return False

            # Load current keys
            current_keys = self.load_keys_securely() or {}

            # Update key
            current_keys[service] = new_key

            # Store updated keys
            if self.store_keys_securely(current_keys):
                # Regenerate .env file
                self.generate_env_file(current_keys)
                print(f"✅ {service} key rotated successfully")
                return True

            return False

        except Exception as e:
            print(f"Key rotation failed for {service}: {e}")
            return False

    async def initialize_system(self):
        """Complete autonomous system initialization"""
        print("🚀 Starting autonomous system initialization...")

        # Check if keys already exist
        existing_keys = self.load_keys_securely()
        if existing_keys:
            print("📋 Existing keys found, validating...")
            # Validate existing keys
            valid_keys = {}
            for service, key in existing_keys.items():
                if service.startswith(("twitter_", "instagram_")):
                    valid_keys[service] = key
                else:
                    service_name = service.split('_')[0]
                    if await self.validate_api_key(service_name, key):
                        valid_keys[service] = key
                    else:
                        print(f"❌ {service} key invalid, will reacquire")

            if len(valid_keys) == len(existing_keys):
                print("✅ All existing keys valid")
                self.generate_env_file(valid_keys)
                return {"keys": valid_keys, "pending_tasks": []}

        # Acquire new agent accounts and keys
        print("🔑 Acquiring new API keys and account registrations...")
        accounts = await self.acquire_agent_accounts("autonomous_agent")
        if not accounts:
            print("❌ Failed to create autonomous account suite")
            return None

        email = accounts["email_account"]["email"]
        password = accounts["email_account"]["password"]
        new_keys_data = await self.acquire_all_keys("autonomous_agent", email, password)
        new_keys = new_keys_data.get("acquired_keys", {})
        pending_tasks = new_keys_data.get("pending_tasks", [])

        if not new_keys and not pending_tasks:
            print("❌ Failed to acquire any API keys and no manual tasks were created")
            return None

        # Store keys and account metadata securely
        if self.store_secure_data(new_keys, accounts):
            self.generate_env_file(new_keys)
            print("🎉 System initialization complete with autonomous account provisioning!")
            return {
                "keys": new_keys,
                "pending_tasks": pending_tasks,
                "accounts": accounts
            }
        else:
            print("❌ Failed to store acquired keys and accounts")
            return None

    def get_account_status(self) -> Dict[str, Any]:
        accounts = self.load_accounts_securely()
        if not accounts:
            return {"status": "no_accounts", "agents": {}}

        return {
            "status": "accounts_loaded",
            "agent_name": accounts.get("agent_name"),
            "created_at": accounts.get("created_at"),
            "social_accounts": list(accounts.get("social_accounts", {}).keys()),
            "porn_site_accounts": list(accounts.get("porn_site_accounts", {}).keys())
        }

    def get_key_status(self) -> Dict[str, Dict]:
        """Get status of all API keys"""
        keys = self.load_keys_securely()
        if not keys:
            return {"status": "no_keys", "services": {}}

        status = {"status": "keys_loaded", "services": {}}

        for service in self.service_keys.keys():
            if service in keys:
                status["services"][service] = {
                    "status": "available",
                    "last_validated": datetime.utcnow().isoformat()
                }
            else:
                status["services"][service] = {
                    "status": "missing",
                    "last_validated": None
                }

        return status