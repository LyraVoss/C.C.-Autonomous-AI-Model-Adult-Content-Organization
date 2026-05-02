import importlib
import sys
from pathlib import Path
from typing import Any, Dict, Optional


class LyraSoulManager:
    def __init__(self, external_root: Optional[Path] = None):
# Stop at the 'external' folder
        self.external_root = Path(external_root) if external_root else Path(__file__).resolve().parents[1] / "external"
        self._ensure_external_path()
        self.soul_module = self._load_soul_module()
        self.initialized = False

    def _ensure_external_path(self) -> None:
        external_package = self.external_root / "Lyra_Soul"
        for path in [self.external_root, external_package]:
            path_str = str(path)
            if path_str not in sys.path:
                sys.path.insert(0, path_str)

    def _load_soul_module(self):
        soul_file = self.external_root / "Lyra_Soul" / "Lyra_Soul.py"
        if not soul_file.exists():
            raise ImportError(f"Lyra_Soul.py not found at expected path: {soul_file}")

        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("lyra_soul_module", soul_file)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not create spec for {soul_file}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as exc:
            raise ImportError(f"Unable to import Lyra_Soul framework: {exc}") from exc

    def initialize(self) -> Dict[str, Any]:
        self.initialized = True
        try:
            context = self.soul_module.get_soul_context()
            return {
                "status": "initialized",
                "model": "Lyra_Soul",
                "context_summary": self.soul_module.get_lexicon_summary(),
                "agent_identity": self.soul_module.IDENTITY,
                "context_keys": list(context.keys()),
            }
        except Exception as exc:
            return {
                "status": "failed",
                "error": str(exc)
            }

    def get_lexicon_summary(self) -> str:
        return self.soul_module.get_lexicon_summary()

    def get_soul_context(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        return self.soul_module.get_soul_context(user_id)

    def refresh_visual_profile(self, allow_hair_length_change: bool = False) -> Dict[str, Any]:
        return self.soul_module.refresh_visual_profile(allow_hair_length_change=allow_hair_length_change)

    def record_donation(self, user_id: str, amount: float, note: Optional[str] = None) -> Dict[str, Any]:
        return self.soul_module.record_donation(user_id, amount, note)

    def get_donation_status(self, user_id: str) -> Dict[str, Any]:
        return self.soul_module.get_donation_status(user_id)

    def update_user_memory(self, user_id: str, **kwargs) -> Dict[str, Any]:
        return self.soul_module.update_user_memory(user_id, **kwargs)
