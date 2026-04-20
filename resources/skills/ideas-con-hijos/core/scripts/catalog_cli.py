# -*- coding: utf-8 -*-
"""CLI for the ideas-con-hijos catalog.

Run from the skill directory:
  python3 scripts/catalog_cli.py stats
  python3 scripts/catalog_cli.py search --query "cartón 10 min"
  python3 scripts/catalog_cli.py show --slug mision-laser-en-el-pasillo
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from catalog import ActivityCatalog, CatalogPaths  # noqa: E402


catalog = ActivityCatalog(CatalogPaths.from_skill_dir(SKILL_DIR))


def cmd_stats(_args: argparse.Namespace) -> int:
    stats = catalog.stats()
    print("Chispas · resumen del catálogo")
    print(f"- total: {stats['total']}")
    print(f"- destacadas: {stats['featured']}")
    print(f"- originales: {stats['internal_original']}")
    print(f"- adaptadas: {stats['adapted_from_source']}")
    print(f"- referencias externas: {stats['external_reference']}")
    print("- tipos principales:")
    for item in stats["top_types"]:
        print(f"  - {item['value']}: {item['count']}")
    return 0


def _print_activity_card(item: dict) -> None:
    print(f"\n{item['title']}  [{item['slug']}]")
    print(f"  {item['age_label']} · {item['duration_label']} · {item['provenance_label']} · {item['delivery_label']}")
    print(f"  tipos: {', '.join(item.get('activity_types', []))}")
    print(f"  materiales: {', '.join(item.get('materials', []))}")
    print(f"  resumen: {item.get('summary', '')}")
    if item.get("source"):
        print(f"  fuente: {item['source']['publisher']} — {item['source']['url']}")


def cmd_search(args: argparse.Namespace) -> int:
    results = catalog.search(
        query=args.query or "",
        activity_type=args.activity_type,
        context=args.context,
        origin=args.origin,
        delivery_mode=args.delivery_mode,
        age=args.age,
        max_duration=args.max_duration,
        featured_only=args.featured_only,
        limit=args.limit,
    )
    print(f"Resultados: {len(results)}")
    for item in results:
        _print_activity_card(item)
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    item = catalog.get(args.slug)
    if not item:
        print(f"No encontrado: {args.slug}")
        return 1

    _print_activity_card(item)
    print(f"\nPor qué funciona: {item.get('why_it_works', '')}")
    if item.get("what_develops"):
        print(f"Desarrolla: {', '.join(item['what_develops'])}")

    print("\nPasos:")
    for idx, step in enumerate(item.get("steps", []), start=1):
        print(f"  {idx}. {step}")

    if item.get("variations"):
        print("\nVariantes:")
        for variation in item["variations"]:
            print(f"  - {variation}")

    if item.get("graphics"):
        print("\nMaterial gráfico / referencias:")
        for asset in item["graphics"]:
            print(f"  - {asset.get('label', asset.get('kind', 'asset'))}: {asset.get('url', '')}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Catálogo de actividades para hacer con hijos")
    subparsers = parser.add_subparsers(dest="command", required=True)

    stats_parser = subparsers.add_parser("stats", help="Resumen del catálogo")
    stats_parser.set_defaults(func=cmd_stats)

    search_parser = subparsers.add_parser("search", help="Buscar actividades")
    search_parser.add_argument("--query", default="", help="Texto libre: cartón, 10 min, calmar, etc.")
    search_parser.add_argument("--activity-type", help="Filtro por tipo: experimento, manualidad, cuento...")
    search_parser.add_argument("--context", help="Filtro por contexto: dia-de-lluvia, antes-de-cenar...")
    search_parser.add_argument("--origin", help="internal_original | adapted_from_source | external_reference")
    search_parser.add_argument("--delivery-mode", help="full_guide | hybrid | external_link")
    search_parser.add_argument("--age", type=int, help="Edad objetivo")
    search_parser.add_argument("--max-duration", type=int, help="Duración máxima en minutos")
    search_parser.add_argument("--limit", type=int, default=10, help="Número máximo de resultados")
    search_parser.add_argument("--featured-only", action="store_true", help="Solo actividades destacadas")
    search_parser.set_defaults(func=cmd_search)

    show_parser = subparsers.add_parser("show", help="Ver una actividad completa")
    show_parser.add_argument("--slug", required=True, help="Slug de la actividad")
    show_parser.set_defaults(func=cmd_show)

    return parser


if __name__ == "__main__":
    parser = build_parser()
    namespace = parser.parse_args()
    raise SystemExit(namespace.func(namespace))
