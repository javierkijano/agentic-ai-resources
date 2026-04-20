import os
import pathlib
import sys
import yaml

class ImprovementCurator:
    def __init__(self, repo_root):
        self.repo_root = pathlib.Path(repo_root)
        # Preparar el path para synergy-finder
        synergy_path = self.repo_root / "resources/skills/synergy-finder/core/logic"
        if str(synergy_path) not in sys.path:
            sys.path.append(str(synergy_path))

    def collect_all_todos(self):
        all_todos = {}
        res_root = self.repo_root / "resources"
        for category in os.listdir(res_root):
            cat_path = res_root / category
            if not cat_path.is_dir(): continue
            for res_id in os.listdir(cat_path):
                todos_path = cat_path / res_id / "core/docs/TODOs.md"
                if todos_path.exists():
                    all_todos[res_id] = todos_path.read_text()
        return all_todos

    def generate_curation_report(self):
        from synergist import SynergyFinder
        synergizer = SynergyFinder(self.repo_root)
        
        todos = self.collect_all_todos()
        report = ["# Global Improvement & Synergy Curation Report\n"]
        report.append(f"Analyzed {len(todos)} resources.\n")
        
        for res_id, content in todos.items():
            report.append(f"## {res_id}")
            
            # Section 1: Backlog de TODOs
            lines = [l for l in content.splitlines() if "[ ]" in l or "[x]" in l]
            if lines:
                report.append("### 💡 Current Backlog")
                for l in lines:
                    report.append(f"  {l}")
            
            # Section 2: Sinergias Proactivas (Nueva!)
            complements = synergizer.find_complements(res_id)
            if complements:
                report.append("### 🚀 Proactive Synergies")
                for c in complements:
                    report.append(f"  - {c}")
            
            report.append("")
        
        return "\n".join(report)

    def save_report(self, report_content):
        report_path = self.repo_root / "runtime/gemini-cli/dev/improvement-manager/curation_report.md"
        os.makedirs(report_path.parent, exist_ok=True)
        report_path.write_text(report_content)
        return report_path
 Joseph
