#!/usr/bin/env python3
import os
import sys
import argparse
import yaml
from logger import log_operation

def create_resource(res_type, res_id):
    base_path = f"resources/{res_type}/{res_id}"
    
    if os.path.exists(base_path):
        log_operation("create_resource", "ERROR", f"Resource {res_id} already exists")
        print(f"ERROR: Resource '{res_id}' of type '{res_type}' already exists at {base_path}")
        sys.exit(1)
    
    # Standard folder structure
    dirs = [
        "core/logic",
        "core/cli",
        "core/webapp",
        "core/docs",
        "core/schemas", # For data/config validation
        "tests",
        "platforms/hermes"
    ]
    
    for d in dirs:
        os.makedirs(os.path.join(base_path, d), exist_ok=True)
    
    # Create resource.yaml with storage, interfaces AND credentials
    resource_data = {
        "id": res_id,
        "kind": res_type.rstrip('s'),
        "status": "draft",
        "description": f"Capability for {res_id}",
        "tags": [f"#{res_type.rstrip('s')}", "#draft"],
        "usage_guidelines": {
            "preferred_scenarios": ["Use when you need to..."],
            "constraints": ["No specific constraints defined"],
            "antipatterns": ["Do not use for..."]
        },
        "platforms": ["hermes", "generic"],
        "interfaces": {
            "cli": {"enabled": True, "commands": {"status": "Check status"}},
            "webapp": {"enabled": False, "port": None, "entrypoint": "app.py"}
        },
        "storage": {
            "standard_layout": True,
            "description": "Standardized runtime storage",
            "contract": "core/docs/STORAGE.md"
        },
        "credentials": [
            {
                "id": "EXAMPLE_API_KEY",
                "type": "secret",
                "description": "An example API key required for this skill",
                "required": False
            }
        ],
        "dependencies": {
            "resources": [],
            "system": [{"id": "python", "version": ">=3.10"}],
            "packages": []
        },
        "dependents": []
    }
    
    with open(os.path.join(base_path, "resource.yaml"), "w") as f:
        yaml.dump(resource_data, f, sort_keys=False)
    
    # Create CREDENTIALS.md guide
    credentials_md = f"""# Credentials Guide: {res_id}

This skill requires the following credentials to function correctly.

## Required Credentials

| ID | Type | Description | Required |
|----|------|-------------|----------|
| `EXAMPLE_API_KEY` | secret | An example API key. | No |

## Setup Instructions
1. Obtain the key from [Service Provider].
2. Provide it via environment variable: `export EXAMPLE_API_KEY=your_key_here`
3. Or place it in the runtime config folder: `runtime/{{context}}/{{env}}/{res_id}/config/credentials.json`
"""
    with open(os.path.join(base_path, "core/docs/CREDENTIALS.md"), "w") as f:
        f.write(credentials_md)

    # Re-use the STORAGE.md creation logic...
    storage_md = f"# Storage Contract: {res_id}\n\nStandard runtime layout required.\n"
    with open(os.path.join(base_path, "core/docs/STORAGE.md"), "w") as f:
        f.write(storage_md)

    # Create TODOs.md
    todos_md = f"""# Improvement Proposals: {res_id}

This file contains suggestions for future improvements identified by agents or humans.
The `improvement-manager` skill will periodically curate this list.

## 💡 Proposed Enhancements
- [ ] Initial capability baseline established.
"""
    with open(os.path.join(base_path, "core/docs/TODOs.md"), "w") as f:
        f.write(todos_md)
    
    # Create README.md
    with open(os.path.join(base_path, "README.md"), "w") as f:
        f.write(f"# {res_id.replace('-', ' ').title()}\n\nDescription for {res_id}.\n")
        
    # Generate initial infra
    from generate_infra import generate_infra
    generate_infra(base_path)
    
    log_operation("create_resource", "SUCCESS", f"Created {res_type}/{res_id} with Storage, Credentials and Infra")
    print(f"SUCCESS: Created resource '{res_id}' with standardized Credentials section.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new agentic resource pack.")
    parser.add_argument("--type", required=True, help="Category (e.g., skills, agents, workflows)")
    parser.add_argument("--id", required=True, help="Resource unique ID (kebab-case)")
    
    args = parser.parse_args()
    create_resource(args.type, args.id)
