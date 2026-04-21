import json
import os
import datetime
from pathlib import Path

class EventTracker:
    def __init__(self, repo_root, agent_id="default", env="dev"):
        self.repo_root = Path(repo_root)
        self.agent_id = agent_id
        self.env = env
        self.resource_id = "analytics-dashboard"
        
    def _get_log_path(self, session_id="current"):
        # Seguir el estándar de runtime de AGENTS.md
        path = self.repo_root / "runtime" / self.agent_id / self.env / self.resource_id / session_id
        path.mkdir(parents=True, exist_ok=True)
        return path / "events.jsonl"

    def log_event(self, action, status="success", metadata=None, session_id="current"):
        event = {
            "timestamp": datetime.datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "action": action,
            "status": status,
            "metadata": metadata or {}
        }
        
        log_file = self._get_log_path(session_id)
        with open(log_file, "a") as f:
            f.write(json.dumps(event) + "\n")
        return event
