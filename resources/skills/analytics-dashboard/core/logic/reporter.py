import json
import os
from pathlib import Path
from collections import Counter

class ActivityReporter:
    def __init__(self, repo_root="."):
        self.repo_root = Path(repo_root).resolve()
        self.runtime_root = self.repo_root / "runtime"

    def scan_events(self):
        all_events = []
        # Asegurar resolución absoluta desde la raíz del repo
        runtime_path = self.runtime_root
        if not runtime_path.exists():
            return []
            
        log_patterns = ["**/events.jsonl", "**/session_registry.jsonl"]
        
        for pattern in log_patterns:
            files = list(runtime_path.glob(pattern))
            for log_file in files:
                try:
                    with open(log_file, "r") as f:
                        for line in f:
                            if line.strip():
                                data = json.loads(line)
                                all_events.append({
                                    "timestamp": data.get("timestamp"),
                                    "agent_id": data.get("agent_id", "system"),
                                    "action": data.get("action") or data.get("operation"),
                                    "status": str(data.get("status", "success")).lower()
                                })
                except Exception as e:
                    print(f"Error reading {log_file}: {e}")
                    continue
        return all_events

    def generate_summary(self):
        events = self.scan_events()
        if not events:
            return "No activity recorded yet."

        total = len(events)
        statuses = Counter(e["status"] for e in events)
        actions = Counter(e["action"] for e in events)
        agents = Counter(e["agent_id"] for e in events)

        report = [
            "# Agent Activity Dashboard Summary",
            f"**Total Events recorded:** {total}",
            "",
            "## Events by Status",
        ]
        for s, count in statuses.items():
            report.append(f"- {s.upper()}: {count}")

        report.append("\n## Top Actions")
        for a, count in actions.most_common(5):
            report.append(f"- {a}: {count}")

        report.append("\n## Active Agents")
        for ag, count in agents.items():
            report.append(f"- {ag}: {count}")

        return "\n".join(report)
