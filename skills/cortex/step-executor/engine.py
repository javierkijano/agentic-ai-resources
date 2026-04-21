#!/usr/bin/env python3
import yaml
import subprocess
import sys
from pathlib import Path
import tempfile
import os
import json
from datetime import datetime

class WorkflowEngine:
    def __init__(self, resources_root):
        self.resources_root = Path(resources_root)
        self.schemas_root = self.resources_root / "protocols/schemas"
        self.manifest = {
            "timestamp": datetime.now().isoformat(),
            "workflow_id": None,
            "steps_audited": [],
            "overall_compliance": True
        }

    def find_workflow(self, workflow_id):
        for folder in ["core", "dev"]:
            path = self.resources_root / f"workflows/{folder}/{workflow_id}/resource.yaml"
            if path.exists():
                return path
        return None

    def log_compliance(self, step_id, schema, success, detail=""):
        self.manifest["steps_audited"].append({
            "step": step_id,
            "schema_validated": schema,
            "status": "PASS" if success else "FAIL",
            "detail": detail
        })
        if not success:
            self.manifest["overall_compliance"] = False

    def validate_structural_contract(self, data, definition_name=None, step_id="init"):
        """Valida datos contra el paquete CUE del ecosistema."""
        if data is None:
            return True

        if not self.schemas_root.exists():
            print(f"⚠️ Aviso: Directorio de esquemas no encontrado.")
            return True

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tf:
            yaml.dump(data, tf)
            temp_path = tf.name

        try:
            # Seleccionar todos los archivos .cue del paquete
            all_schemas = list(self.schemas_root.glob("*.cue"))
            cmd = ["cue", "vet", temp_path] + [str(s) for s in all_schemas]
            
            if definition_name:
                cmd.extend(["-d", f"#{definition_name}"])

            result = subprocess.run(cmd, capture_output=True, text=True)
            success = result.returncode == 0
            self.log_compliance(step_id, definition_name or "Generic", success, result.stderr if not success else "OK")
            
            if not success:
                print(f"❌ Error de Validación Estructural (CUE): {definition_name}")
                print(result.stderr)
            return success
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def save_manifest(self):
        workspace_runtime = Path("/home/jq-hermes-01/git-repositories/own/agentic-ai-workspace/runtime/compliance")
        workspace_runtime.mkdir(parents=True, exist_ok=True)
        filename = f"execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        manifest_path = workspace_runtime / filename
        with open(manifest_path, "w") as f:
            json.dump(self.manifest, f, indent=2)
        print(f"\n📜 [COMPLIANCE] Manifiesto de Ejecución Certificada generado.")
        print(f"   Resultado Global: {'✅ PASS' if self.manifest['overall_compliance'] else '❌ FAIL'}")
        print(f"   Evidencia: {manifest_path}")

    def execute_workflow(self, workflow_id, context=None, is_preview=False):
        context = context or {}
        if not is_preview:
            self.manifest["workflow_id"] = workflow_id
            print(f"\n🧠 [CORTEX] Ejecutando: {workflow_id}")
            # Validar integridad del contexto inicial
            self.validate_structural_contract(context, "Context", "context-init")
        else:
            print(f"  📂 Workflow Planificado: {workflow_id}")

        wf_path = self.find_workflow(workflow_id)
        if not wf_path:
            print(f"❌ Error: Workflow '{workflow_id}' no encontrado.")
            return False

        with open(wf_path, "r") as f:
            config = yaml.safe_load(f)

        # 1. Validación de Estado Previo
        state_v = config.get("state_validation", {})
        if not is_preview and state_v.get("pre_state_schema"):
            self.validate_structural_contract(context.get("workspace_state", {}), state_v["pre_state_schema"], "pre-state")

        steps = config.get("steps", [])
        for step in steps:
            prefix = "    └─" if is_preview else "  ▶️ Paso:"
            print(f"{prefix} {step.get('id')} ({step.get('intent')[:60]}...)")

            # 2. Validación de Input
            step_v = step.get("validation", {})
            if not is_preview and step_v.get("input_schema"):
                self.validate_structural_contract(context.get("last_input", {}), step_v["input_schema"], step['id'])

            associations = step.get("associations", [])
            if associations:
                best = sorted(associations, key=lambda x: x.get('strength', 0), reverse=True)[0]
                if "workflow" in best:
                    self.execute_workflow(best["workflow"], context, is_preview=is_preview)
                elif not is_preview:
                    print(f"     🛠 Herramienta Seleccionada: {best.get('tool')} (Fuerza: {best.get('strength')})")

            # 3. Validación de Output
            if not is_preview and step_v.get("output_schema"):
                self.validate_structural_contract(context.get("last_output", {}), step_v["output_schema"], step['id'])

        # 4. Validación de Estado Posterior
        if not is_preview and state_v.get("post_state_schema"):
             self.validate_structural_contract(context.get("workspace_state", {}), state_v["post_state_schema"], "post-state")

        if not is_preview:
            print(f"\n✅ Workflow '{workflow_id}' finalizado.")
            self.save_manifest()
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: engine.py <workflow_id>")
        sys.exit(1)

    wf_id = sys.argv[1]
    engine = WorkflowEngine("/home/jq-hermes-01/git-repositories/own/agentic-ai-resources")

    print(f"\n🗺 [PLAN] Previsualizando el mapa de ejecución para '{wf_id}':")
    engine.execute_workflow(wf_id, is_preview=True)

    print("\n--- Iniciando ejecución real ---")
    engine.execute_workflow(wf_id, is_preview=False)

