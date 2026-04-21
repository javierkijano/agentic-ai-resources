#!/usr/bin/env python3
import os
import yaml
import sys
import pathlib

def generate_infra(res_path):
    res_path = pathlib.Path(res_path)
    yaml_path = res_path / "resource.yaml"
    
    if not yaml_path.exists():
        return
        
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    deps = data.get('dependencies', {})
    infra_dir = res_path / "core" / "infra"
    os.makedirs(infra_dir, exist_ok=True)
    
    # 1. Generate requirements.txt (for Python/pip)
    pip_packages = [p for p in deps.get('packages', []) if p.get('manager') == 'pip']
    if pip_packages:
        req_content = "\n".join([f"{p['name']}{p.get('version', '')}" for p in pip_packages])
        with open(infra_dir / "requirements.txt", "w") as f:
            f.write(req_content + "\n")
        print(f"  - Generated requirements.txt")

    # 2. Generate Dockerfile
    system_deps = [s['id'] for s in deps.get('system', [])]
    if system_deps or pip_packages:
        docker_lines = [
            "FROM python:3.10-slim",
            "WORKDIR /app",
            "RUN apt-get update && apt-get install -y " + " ".join([s for s in system_deps if s != 'python']) + " && rm -rf /var/lib/apt/lists/*" if len(system_deps) > 1 else "",
            "COPY core/infra/requirements.txt ." if pip_packages else "",
            "RUN pip install --no-cache-dir -r requirements.txt" if pip_packages else "",
            "COPY . .",
            "CMD [\"python\", \"core/cli/main.py\"]"
        ]
        with open(infra_dir / "Dockerfile", "w") as f:
            f.write("\n".join([l for l in docker_lines if l]) + "\n")
        print(f"  - Generated Dockerfile")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: generate_infra.py <resource_path>")
        sys.exit(1)
    generate_infra(sys.argv[1])
