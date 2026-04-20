import os
import yaml
import pathlib

class RepoExplorer:
    def __init__(self, repo_root):
        self.repo_root = pathlib.Path(repo_root)

    def get_onboarding_summary(self):
        agents_md = self.repo_root / "AGENTS.md"
        if agents_md.exists():
            return agents_md.read_text()
        return "No AGENTS.md found. Please check docs/ for rules."

    def list_all_resources(self):
        resources = []
        res_root = self.repo_root / "resources"
        if not res_root.exists():
            return []
            
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
                            "tags": data.get("tags", [])
                        })
        return resources

    def find_skill_by_tag(self, tag):
        all_res = self.list_all_resources()
        return [r for r in all_res if tag in r["tags"]]
