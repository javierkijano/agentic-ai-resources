#!/usr/bin/env python3
import sys
import os
import pathlib
import argparse

# Configurar paths para importar lógica del repository-manager
scripts_dir = pathlib.Path(__file__).parent
repo_root = scripts_dir.parent
logic_path = repo_root / "resources/skills/repository-manager/core/logic"
sys.path.append(str(logic_path))

try:
    from explorer import RepoExplorer
except ImportError:
    print("Error: No se pudo cargar la lógica de RepoExplorer.")
    sys.exit(1)

def main():
    explorer = RepoExplorer(repo_root)
    
    parser = argparse.ArgumentParser(description="Explorador de recursos Agentic.")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando: list
    list_parser = subparsers.add_parser("list", help="Listar todos los recursos")
    list_parser.add_argument("--tags", action="store_true", help="Agrupar por hashtags")

    # Comando: advice
    advice_parser = subparsers.add_parser("advice", help="Obtener consejos de uso para un recurso")
    advice_parser.add_argument("id", help="ID del recurso (kebab-case)")

    # Comando: workflow
    workflow_parser = subparsers.add_parser("workflow", help="Consultar el checklist obligatorio para un tipo de cambio")
    workflow_parser.add_argument("type", choices=["NEW_RESOURCE", "LOGIC_UPDATE", "CROSS_CUTTING", "SECURITY_FIX", "PLATFORM_OVERLAY"], help="Tipo de cambio")

    # Comando: status
    subparsers.add_parser("status", help="Resumen de actividad y huella del repositorio")

    args = parser.parse_args()

    if args.command == "list":
        if args.tags:
            themed = explorer.list_all_resources(group_by_tag=True)
            for tag, resources in sorted(themed.items()):
                print(f"\n{tag}:")
                for r in resources:
                    print(f"  - {r['id']} ({r['kind']})")
        else:
            resources = explorer.list_all_resources()
            print(f"{'ID':<35} | {'KIND':<15} | {'DESCRIPTION'}")
            print("-" * 80)
            for r in sorted(resources, key=lambda x: x['id']):
                desc = r['description'][:50] + "..." if len(r['description']) > 50 else r['description']
                print(f"{r['id']:<35} | {r['kind']:<15} | {desc}")

    elif args.command == "advice":
        print(explorer.get_selection_advice(args.id))

    elif args.command == "workflow":
        try:
            from workflows import WorkflowRegistry
            wr = WorkflowRegistry(repo_root)
            print(wr.get_workflow(args.type))
        except ImportError:
            print("Error: No se pudo cargar la lógica de Workflows.")

    elif args.command == "status":
        footprint = explorer.get_runtime_footprint()
        print("--- REPOSITORY STATUS & FOOTPRINT ---")
        for key, val in footprint.items():
            print(f"{key.replace('_', ' ').upper()}: {val}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
