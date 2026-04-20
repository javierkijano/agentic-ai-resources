import os
import yaml
import pathlib
from collections import defaultdict

class RepoExplorer:
    def __init__(self, repo_root):
        self.repo_root = pathlib.Path(repo_root)

    def get_onboarding_summary(self):
        agents_md = self.repo_root / "AGENTS.md"
        if agents_md.exists():
            return agents_md.read_text()
        return "No AGENTS.md found. Please check docs/ for rules."

    def list_all_resources(self, group_by_tag=False):
        resources = []
        res_root = self.repo_root / "resources"
        if not res_root.exists(): return []
            
        for category in os.listdir(res_root):
            cat_path = res_root / category
            if not cat_path.is_dir(): continue
            
            for res_id in os.listdir(cat_path):
                yaml_path = cat_path / res_id / "resource.yaml"
                if yaml_path.exists():
                    with open(yaml_path, 'r') as f:
                        data = yaml.safe_load(f)
                        resources.append({
                            "id": data.get("id"),
                            "kind": data.get("kind"),
                            "description": data.get("description", "No description"),
                            "tags": [t if t.startswith('#') else f'#{t}' for t in data.get("tags", [])],
                            "guidelines": data.get("usage_guidelines", {}),
                            "dependents": data.get("dependents", [])
                        })
        
        if not group_by_tag:
            return resources

        # Agrupar por hashtag
        themed_resources = defaultdict(list)
        for res in resources:
            for tag in res["tags"]:
                themed_resources[tag].append(res)
        return dict(themed_resources)

    def get_selection_advice(self, resource_id):
        """Devuelve consejos específicos para que el agente decida si usar esta skill."""
        res = self.find_resource_by_id(resource_id)
        if not res: return "Resource not found."
        
        g = res.get("guidelines", {})
        advice = [f"--- Selection Advice for {resource_id} ---"]
        advice.append(f"RECOMMENDED FOR: {', '.join(g.get('preferred_scenarios', []))}")
        advice.append(f"CONSTRAINTS: {', '.join(g.get('constraints', []))}")
        advice.append(f"ANTIPATTERNS: {', '.join(g.get('antipatterns', []))}")
        return "\n".join(advice)

    def find_resource_by_id(self, resource_id):
        all_res = self.list_all_resources()
        return next((r for r in all_res if r["id"] == resource_id), None)
