import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from .ai_model_framework import AIModelFrameworkTemplate


class AIModelManager:
    def __init__(self, registry_file: str = ".ai_models.json"):
        self.registry_path = Path(registry_file)
        self.framework = AIModelFrameworkTemplate()
        self.models: Dict[str, Dict[str, Any]] = self._load_registry()

    def _load_registry(self) -> Dict[str, Dict[str, Any]]:
        if not self.registry_path.exists():
            return {}
        try:
            data = json.loads(self.registry_path.read_text())
            return data.get("models", {})
        except Exception:
            return {}

    def _save_registry(self) -> None:
        payload = {"models": self.models, "updated_at": datetime.utcnow().isoformat()}
        self.registry_path.write_text(json.dumps(payload, indent=2))
        self.registry_path.chmod(0o600)

    def create_model(self, base_name: str, archetype: Optional[str] = None, niche: Optional[str] = None) -> Dict[str, Any]:
        new_model = self.framework.create_personality(base_name, archetype=archetype, niche=niche)
        self.models[new_model["identity"]["unique_id"]] = new_model
        self._save_registry()
        return new_model

    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        return self.models.get(model_id)

    def list_models(self) -> List[Dict[str, Any]]:
        return list(self.models.values())

    def delete_model(self, model_id: str) -> bool:
        if model_id in self.models:
            del self.models[model_id]
            self._save_registry()
            return True
        return False
