import asyncio
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

class InterventionManager:
    def __init__(self, store_file: str = ".intervention_tasks.json"):
        self.store_file = Path(store_file)
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self._futures: Dict[str, asyncio.Future] = {}
        self._load_tasks()

    def _load_tasks(self) -> None:
        if not self.store_file.exists():
            return

        try:
            data = json.loads(self.store_file.read_text())
            self.tasks = data.get("tasks", {})
        except Exception:
            self.tasks = {}

    def _persist_tasks(self) -> None:
        stored = {"tasks": self.tasks}
        self.store_file.write_text(json.dumps(stored, indent=2))
        self.store_file.chmod(0o600)

    def add_task(self,
                 service: str,
                 agent_name: str,
                 email: Optional[str],
                 description: str,
                 details: Optional[Dict[str, Any]] = None) -> str:
        task_id = uuid.uuid4().hex
        task = {
            "id": task_id,
            "service": service,
            "agent_name": agent_name,
            "email": email,
            "description": description,
            "details": details or {},
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "result": None
        }

        self.tasks[task_id] = task
        self._persist_tasks()
        return task_id

    def get_tasks(self) -> List[Dict[str, Any]]:
        return list(self.tasks.values())

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self.tasks.get(task_id)

    def resolve_task(self, task_id: str, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]
        task["status"] = "resolved"
        task["result"] = result
        task["updated_at"] = datetime.utcnow().isoformat()
        self._persist_tasks()

        future = self._futures.get(task_id)
        if future and not future.done():
            future.set_result(task)

        return task

    async def wait_for_task(self, task_id: str, timeout: float = 86400.0) -> Optional[Dict[str, Any]]:
        existing = self.tasks.get(task_id)
        if existing and existing["status"] == "resolved":
            return existing

        loop = asyncio.get_event_loop()
        future = self._futures.get(task_id)
        if not future:
            future = loop.create_future()
            self._futures[task_id] = future

        try:
            result = await asyncio.wait_for(future, timeout)
            return result
        except asyncio.TimeoutError:
            return None

    def get_task_summary(self) -> Dict[str, Any]:
        pending = [t for t in self.tasks.values() if t["status"] == "pending"]
        resolved = [t for t in self.tasks.values() if t["status"] == "resolved"]
        return {
            "pending_count": len(pending),
            "resolved_count": len(resolved),
            "pending_tasks": pending,
            "resolved_tasks": resolved
        }
