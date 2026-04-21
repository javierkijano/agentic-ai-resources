#!/usr/bin/env python3
import os
import pathlib
import json

class DeepResearcher:
    def __init__(self, roots, task_query):
        self.roots = [pathlib.Path(r) for r in roots]
        self.query = task_query.lower()
        self.results = []
        self.log_path = pathlib.Path("runtime/research_log.jsonl")

    def map_and_analyze(self, path, depth=0):
        """Recursión infinita (con límite de seguridad) para mapear y analizar."""
        if depth > 10: return # Límite de seguridad
        
        # 1. Listar elementos del nivel actual
        try:
            items = list(path.iterdir())
        except PermissionError:
            return

        for item in items:
            # Ignorar carpetas ocultas o de sistema
            if item.name.startswith('.') or item.name == "runtime" or item.name == "vendor":
                continue

            # 2. Investigar relevancia
            relevance = self.check_relevance(item)
            
            if relevance:
                finding = {
                    "path": str(item),
                    "depth": depth,
                    "relevance_score": relevance,
                    "type": "file" if item.is_file() else "directory"
                }
                self.results.append(finding)
                self.log_finding(finding)

            # 3. Recursión
            if item.is_dir():
                self.map_and_analyze(item, depth + 1)

    def check_relevance(self, item):
        """Analiza si el elemento tiene relación con la tarea."""
        # Simple heurística por ahora: coincidencia de nombre o contenido
        score = 0
        if self.query in item.name.lower():
            score += 50
        
        if item.is_file() and item.suffix in ['.py', '.md', '.yaml']:
            try:
                content = item.read_text(errors='ignore').lower()
                if self.query in content:
                    score += 50
            except:
                pass
        
        return score if score > 0 else None

    def log_finding(self, finding):
        """Guarda la relación en un log temporal."""
        # Asegurar que el directorio runtime existe (en el workspace normalmente)
        print(f"    🔍 Hallazgo: {finding['path']} (Relevancia: {finding['relevance_score']})")

    def run(self):
        print(f"🚀 Iniciando investigación profunda para: '{self.query}'")
        for root in self.roots:
            print(f"  📂 Escaneando raíz: {root}")
            self.map_and_analyze(root)
        print(f"\n✅ Investigación completada. {len(self.results)} elementos relevantes encontrados.")

if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "philosophy"
    researcher = DeepResearcher(["/home/jq-hermes-01/git-repositories/own/agentic-ai-resources"], query)
    researcher.run()
