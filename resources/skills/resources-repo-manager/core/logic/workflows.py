import yaml
from pathlib import Path

class WorkflowRegistry:
    def __init__(self, repo_root):
        self.repo_root = Path(repo_root)
        self.workflows_path = self.repo_root / "resources/skills/repository-manager/core/docs/WORKFLOWS.md"

    def get_workflow(self, change_type: str) -> str:
        """Returns the specific workflow/checklist for a given change type."""
        content = self.workflows_path.read_text()
        
        # Simple extraction logic based on headers
        sections = content.split("### ")
        for section in sections:
            # Match if the change_type is in the header (e.g. "1. NEW_RESOURCE")
            header_line = section.split("\n")[0]
            if change_type in header_line:
                return "### " + section.split("\n\n###")[0].strip()
        
        return f"Workflow for '{change_type}' not found. Please refer to {self.workflows_path}"

    def list_change_types(self) -> list[str]:
        """Lists available change types."""
        return ["NEW_RESOURCE", "LOGIC_UPDATE", "CROSS_CUTTING", "SECURITY_FIX", "PLATFORM_OVERLAY"]
