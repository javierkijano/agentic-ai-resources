import json
from pathlib import Path
from collections import Counter

class WorkflowAuditor:
    def __init__(self, repo_root):
        self.repo_root = Path(repo_root)
        self.runtime_root = self.repo_root / "runtime"
        self.workflows_path = self.repo_root / "resources/skills/repository-manager/core/docs/WORKFLOWS.md"

    def analyze_execution_gaps(self):
        """Compares logs vs workflows to find inefficiencies."""
        events = []
        
        # Scan for both standard events and session registry logs
        log_patterns = ["**/events.jsonl", "**/session_registry.jsonl"]
        
        for pattern in log_patterns:
            for log_file in self.runtime_root.glob(pattern):
                try:
                    with open(log_file, "r") as f:
                        for line in f:
                            if line.strip():
                                data = json.loads(line)
                                # Normalize fields between different log types
                                events.append({
                                    "action": data.get("action") or data.get("operation"),
                                    "status": data.get("status").lower() if data.get("status") else "unknown",
                                    "details": data.get("details", "")
                                })
                except Exception:
                    continue
        
        if not events:
            return "No logs found to audit."

        errors = [e for e in events if "error" in e["status"] or "failure" in e["status"] or "alert" in e["status"]]
        actions = [e["action"] for e in events]
        
        suggestions = ["# Workflow Audit Report\n"]
        
        # Pattern 1: High failure rate in specific actions
        error_counts = Counter(e["action"] for e in errors)
        for action, count in error_counts.items():
            if count > 2:
                suggestions.append(f"### [!] BOTTLENECK: {action}")
                suggestions.append(f"- Detected {count} errors. Consider adding a 'Pre-flight check' to the relevant workflow.\n")

        # Pattern 2: Missing automated steps
        if "validate_repo" not in actions and len(actions) > 5:
            suggestions.append("### [!] PROTOCOL GAP: Validation")
            suggestions.append("- Multiple actions recorded without a corresponding 'validate_repo' call. Ensure the 'Validation' step is prominent in all checklists.\n")

        # Pattern 3: Improvement for NEW_RESOURCE
        if "create_resource" in actions:
            suggestions.append("### [?] IMPROVEMENT: NEW_RESOURCE")
            suggestions.append("- Logic implementation and testing are often separated by many steps. Consider suggesting 'Test-Driven Scaffolding'.\n")

        if len(suggestions) <= 1:
            return "Audit complete: Workflows appear aligned with execution patterns."
            
        return "\n".join(suggestions)

if __name__ == "__main__":
    auditor = WorkflowAuditor(".")
    print(auditor.analyze_execution_gaps())
