#!/usr/bin/env python3
import sys
import os
import argparse
from pathlib import Path

# Configurar paths para importar lógica
core_dir = Path(__file__).parent.parent
sys.path.append(str(core_dir / "logic"))

try:
    from reporter import ActivityReporter
    from tracker import EventTracker
except ImportError as e:
    print(f"Error: No se pudo cargar la lógica: {e}")
    sys.exit(1)

def main():
    repo_root = "."
    parser = argparse.ArgumentParser(description="Analytics Dashboard CLI")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando: report
    subparsers.add_parser("report", help="Generar un informe de actividad acumulada")

    # Comando: log
    log_parser = subparsers.add_parser("log", help="Registrar un evento manualmente")
    log_parser.add_argument("action", help="Nombre de la acción")
    log_parser.add_argument("--status", default="success", help="Estado (success/error)")

    args = parser.parse_args()

    if args.command == "report":
        reporter = ActivityReporter(repo_root)
        print(reporter.generate_summary())
    
    elif args.command == "log":
        tracker = EventTracker(repo_root)
        event = tracker.log_event(args.action, status=args.status)
        print(f"Evento registrado: {event['timestamp']} | {event['action']} | {event['status']}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
