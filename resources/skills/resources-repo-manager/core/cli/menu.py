#!/usr/bin/env python3
import os
import sys
import pathlib

# Configurar paths para importar lógica
core_dir = pathlib.Path(__file__).parent.parent
sys.path.append(str(core_dir / "logic"))

# Imports de lógica (asumiendo que los archivos están en core/logic/)
from explorer import RepoExplorer
from doc_expert import DocExpert
# Nota: Importamos el resto según sea necesario

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    print("="*60)
    print("      AGENTIC RESOURCES - REPOSITORY COMMAND CENTER")
    print("="*60)

def main_menu():
    repo_root = core_dir.parent.parent.parent.parent
    explorer = RepoExplorer(repo_root)
    docs = DocExpert(repo_root)

    while True:
        clear_screen()
        print_header()
        print("\n[1] EXPLORAR: Listar habilidades y recursos")
        print("[2] DOCUMENTACIÓN: Consultar guías y reglas")
        print("[3] INTEGRIDAD: Validar estructura y limpieza")
        print("[4] GESTIÓN: Crear recurso o Generar Infra")
        print("[5] GIT: Preparar mensaje de commit")
        print("[6] CURACIÓN: Analizar y consolidar TODOs")
        print("[7] SEGURIDAD: Auditoría de Secretos y PII")
        print("\n[0] SALIR")
        
        choice = input("\nSeleccione una opción: ")

        if choice == '1':
            clear_screen()
            print("--- EXPLORACIÓN DE RECURSOS ---")
            print("[1] Listar todos")
            print("[2] Agrupar por #Hashtag")
            print("[3] Ver Guía de Selección (Consejos de uso)")
            sub_choice = input("\nOpción: ")
            
            if sub_choice == '1':
                for res in explorer.list_all_resources():
                    print(f"[{res['kind'].upper()}] {res['id']}: {res['description'][:50]}...")
            elif sub_choice == '2':
                themed = explorer.list_all_resources(group_by_tag=True)
                for tag, resources in themed.items():
                    print(f"\n{tag}:")
                    for r in resources:
                        print(f"  - {r['id']}")
            elif sub_choice == '3':
                rid = input("\nIntroduce el ID del recurso: ")
                print("\n" + explorer.get_selection_advice(rid))
            
            input("\nPresione Enter para volver...")

        elif choice == '2':
            clear_screen()
            print("--- DOCUMENTACIÓN DISPONIBLE ---")
            available_docs = docs.list_docs()
            for i, d in enumerate(available_docs):
                print(f"[{i}] {d}")
            
            doc_choice = input("\nSeleccione un número para leer (o Enter para volver): ")
            if doc_choice.isdigit() and int(doc_choice) < len(available_docs):
                clear_screen()
                print(f"--- CONTENIDO DE {available_docs[int(doc_choice)]} ---\n")
                print(docs.read_doc(available_docs[int(doc_choice)]))
                input("\nPresione Enter para volver...")

        elif choice == '3':
            clear_screen()
            # Llamada al validador (importación local para evitar bucles)
            import validate_repo
            validate_repo.main() # Asumiendo que main existe
            input("\nPresione Enter para volver...")

        elif choice == '4':
            clear_screen()
            print("[1] Crear nuevo recurso")
            print("[2] Regenerar infraestructura (Docker/Pip)")
            m_choice = input("\nOpción: ")
            if m_choice == '1':
                rtype = input("Tipo (skills, agents, etc): ")
                rid = input("ID (kebab-case): ")
                import create_resource
                create_resource.create_resource(rtype, rid)
            elif m_choice == '2':
                rid = input("ID del recurso: ")
                # Buscar path del recurso y llamar a generate_infra
                import generate_infra
                # Aquí necesitaríamos lógica para encontrar el path, simplificado:
                # generate_infra.generate_infra(f'resources/skills/{rid}')
            input("\nPresione Enter para volver...")

        elif choice == '5':
            clear_screen()
            import describe_changes
            # Aquí necesitaríamos adaptar describe_changes para ser llamado como función
            os.system('python3 ' + str(core_dir / "logic/describe_changes.py"))
            input("\nPresione Enter para volver...")

        elif choice == '6':
            clear_screen()
            print("--- CURACIÓN DE MEJORAS ---")
            sys.path.append(str(repo_root / "resources/skills/improvement-manager/core/logic"))
            try:
                from curator import ImprovementCurator
                curator = ImprovementCurator(repo_root)
                print("Analizando todos los TODOs.md del repositorio...")
                report = curator.generate_curation_report()
                report_path = curator.save_report(report)
                print(f"\nÉxito. Informe generado en:\n{report_path}")
                print("\nResumen del informe:")
                print("-" * 20)
                print("\n".join(report.splitlines()[:20])) # Primeras 20 líneas
            except ImportError:
                print("Error: No se pudo cargar la lógica del curador.")
            input("\nPresione Enter para volver...")

        elif choice == '7':
            clear_screen()
            print("--- AUDITORÍA DE SEGURIDAD (PII & SECRETS) ---")
            try:
                from security_scanner import SecurityScanner
                scanner = SecurityScanner(repo_root)
                print("Escaneando todo el repositorio (esto puede tardar)...")
                findings = scanner.run_full_scan()
                if findings:
                    print(f"\nALERTA: Se han encontrado {len(findings)} posibles riesgos:")
                    for f in findings:
                        print(f"  [!] {f['type']} -> {f['file']}:{f['line']}")
                    print("\nRECOMENDACIÓN: Mueve estos secretos a archivos en runtime/config o usa variables de entorno.")
                else:
                    print("\nSUCCESS: No se han detectado secretos ni PII en el código.")
            except ImportError:
                print("Error: No se pudo cargar el motor de seguridad.")
            input("\nPresione Enter para volver...")

        elif choice == '0':
            print("\n¡Hasta pronto!")
            break

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.")
