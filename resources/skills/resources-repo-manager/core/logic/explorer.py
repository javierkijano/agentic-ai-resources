import os
import yaml
import pathlib
from collections import defaultdict

class RepoExplorer:
    def __init__(self, repo_root):
        self.repo_root = pathlib.Path(repo_root)

    def get_runtime_footprint(self):
        return "No runtime data found in canonical resources (expected behavior)."

    def list_all_resources(self, group_by_tag=False, external_paths=None):
        resources = []
        search_paths = [self.repo_root / "resources"]
        
        if external_paths:
            for p in external_paths:
                search_paths.append(pathlib.Path(p))

        for res_root in search_paths:
            if not res_root.exists(): continue
            
            # Escanear recursivamente hasta 2 niveles para encontrar resource.yaml
            for root, dirs, files in os.walk(res_root):
                # Limitar profundidad para eficiencia
                depth = len(pathlib.Path(root).relative_to(res_root).parts)
                if depth > 2: continue
                
                if "resource.yaml" in files:
                    yaml_path = pathlib.Path(root) / "resource.yaml"
                    try:
                        with open(yaml_path, 'r') as f:
                            data = yaml.safe_load(f)
                            if data and "id" in data:
                                resources.append({
                                    "id": data.get("id"),
                                    "kind": data.get("kind"),
                                    "description": data.get("description", "No description"),
                                    "tags": [t if t.startswith('#') else f'#{t}' for t in data.get("tags", [])]
                                })
                    except Exception:
                        continue
        
        if not group_by_tag:
            return resources

        themed_resources = defaultdict(list)
        for res in resources:
            for tag in res["tags"]:
                themed_resources[tag].append(res)
        return dict(themed_resources)

    def get_selection_advice(self, resource_id):
        return "Advice logic under refactoring for multi-repo support."
