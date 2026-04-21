#!/usr/bin/env python3
import yaml
import subprocess
import sys
import os
from pathlib import Path

class WorkflowEngine:
    def __init__(self, resources_root, workspace_root=None):
        self.resources_root = Path(resources_root)
        self.workspace_root = Path(workspace_root) if workspace_root else None

    def execute_workflow(self, workflow_id, context=None):
        print(f"\n🚀 Iniciando Workflow: {workflow_id}")
        wf_path = self.resources_root / f"resources/workflows/{workflow_id}/resource.yaml"
        
        if not wf_path.exists():
            print(f"❌ Error: Workflow '{workflow_id}' no encontrado en {wf_path}")
            return False

        with open(wf_path, "r") as f:
            config = yaml.safe_load(f)

        steps = config.get("steps", [])
        for step in steps:
            step_id = step.get("id", "unnamed-step")
            print(f"\n  [Paso: {step_id}]")
            
            if "workflow" in step:
                if not self.execute_workflow(step["workflow"], context): return False
            elif "skill" in step:
                print(f"    🛠 Invocando Skill: {step['skill']} -> {step.get('command')}")
            elif "shell" in step:
                cmd = os.path.expandvars(step["shell"])
                print(f"    🐚 Ejecutando Shell: {cmd}")
                try:
                    subprocess.run(cmd, shell=True, check=True, cwd=self.resources_root)
                except Exception as e:
                    print(f"    ❌ Error: {e}")
                    return False
        return True

if __name__ == "__main__":
    import sys
    wf_id = sys.argv[1] if len(sys.argv) > 1 else "comprehensive-system-research"
    root = os.environ.get("AGENTIC_RESOURCES", "/home/jq-hermes-01/git-repositories/own/agentic-ai-resources")
    # Si estamos en un worktree, el root cambia. 
    # Para el test usaremos la ruta del worktree actual si existe.
    worktree_root = "/home/jq-hermes-01/hermes-workspace/agentic-ai-resources/task-system-research-workflow"
    engine = WorkflowEngine(worktree_root if Path(worktree_root).exists() else root)
    engine.execute_workflow(wf_id)
