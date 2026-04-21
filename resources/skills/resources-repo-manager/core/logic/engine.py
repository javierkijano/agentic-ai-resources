#!/usr/bin/env python3
import yaml
import subprocess
from pathlib import Path

class WorkflowEngine:
    def __init__(self, resources_root, workspace_root=None):
        self.resources_root = Path(resources_root)
        self.workspace_root = Path(workspace_root) if workspace_root else None

    def execute_workflow(self, workflow_id, context=None):
        """
        Busca un workflow por ID y ejecuta sus pasos de forma secuencial.
        Soporta anidamiento de otros workflows.
        """
        print(f"\n🚀 Iniciando Workflow: {workflow_id}")
        wf_path = self.resources_root / f"resources/workflows/{workflow_id}/resource.yaml"
        
        if not wf_path.exists():
            print(f"❌ Error: Workflow '{workflow_id}' no encontrado en {wf_path}")
            return False

        with open(wf_path, "r") as f:
            config = yaml.safe_load(f)

        steps = config.get("steps", [])
        if not steps:
            print(f"⚠️ El workflow '{workflow_id}' no define pasos ejecutables.")
            return True

        for step in steps:
            step_id = step.get("id", "unnamed-step")
            print(f"\n  [Paso: {step_id}]")
            
            # Caso 1: El paso es un sub-workflow (ANIDAMIENTO)
            if "workflow" in step:
                success = self.execute_workflow(step["workflow"], context)
                if not success: return False
                
            # Caso 2: El paso invoca una Skill
            elif "skill" in step:
                success = self.invoke_skill(step["skill"], step.get("command"), context)
                if not success: return False
                
            # Caso 3: Comando directo de sistema (emergencia)
            elif "shell" in step:
                success = self.run_shell(step["shell"], context)
                if not success: return False

        print(f"\n✅ Workflow '{workflow_id}' completado con éxito.")
        return True

    def invoke_skill(self, skill_id, command, context):
        """Busca y ejecuta un comando de una skill."""
        print(f"    🛠 Invocando Skill: {skill_id} -> {command}")
        # Aquí iría la lógica de resolución de paths de la skill y ejecución
        # Por ahora simulamos la llamada para validar la arquitectura de flujo
        return True

    def run_shell(self, command, context):
        """Ejecuta un comando shell directamente."""
        print(f"    🐚 Ejecutando Shell: {command}")
        try:
            subprocess.run(command, shell=True, check=True)
            return True
        except Exception as e:
            print(f"    ❌ Error en shell: {e}")
            return False

if __name__ == "__main__":
    engine = WorkflowEngine("/home/jq-hermes-01/git-repositories/own/agentic-ai-resources")
    engine.execute_workflow("add-skill")
