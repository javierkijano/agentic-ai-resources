import json
import os
from pathlib import Path
from collections import Counter

class ActivityReporter:
    def __init__(self, repo_root):
        self.repo_root = Path(repo_root)
        self.runtime_root = self.repo_root / "runtime"

    def scan_events(self):
        all_events = []
        if not self.runtime_root.exists():
            return []
            
        for log_file in self.runtime_root.glob("**/analytics-dashboard/**/events.jsonl"):
            try:
                with open(log_file, "r") as f:
                    for line in f:
                        if line.strip():
                            all_events.append(json.loads(line))
            except Exception:
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
