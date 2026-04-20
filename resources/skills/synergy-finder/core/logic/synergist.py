import os
import pathlib

class SynergyFinder:
    def __init__(self, repo_root):
        self.repo_root = pathlib.Path(repo_root)
        # Diccionario conceptual de sinergias (base de conocimiento interna)
        self.synergy_map = {
            "linkedin": ["image-generator", "content-scheduler", "lead-scraper"],
            "google-workspace-assistant": ["slack-integration", "notion-sync", "task-prioritizer"],
            "x-remote-control": ["trending-topic-analyzer", "meme-generator"],
            "adhd-assistant": ["pomodoro-timer", "voice-to-text", "zen-mode-controller"],
            "chrome-remote-browser-control": ["stealth-proxy-manager", "captcha-solver"]
        }

    def find_complements(self, resource_id):
        """Busca sugerencias proactivas para una skill específica."""
        # 1. Buscar en el mapa interno
        suggestions = self.synergy_map.get(resource_id, ["general-utilities", "analytics-dashboard"])
        
        # 2. Verificar si ya existen en el repo
        repo_skills = self._get_installed_skills()
        
        proactive_ideas = []
        for sug in suggestions:
            if sug in repo_skills:
                proactive_ideas.append(f"INTEGRACIÓN: Ya tienes '{sug}', podrías conectarlo.")
            else:
                proactive_ideas.append(f"EXPANSIÓN: Se recomienda crear o importar '{sug}'.")
                
        return proactive_ideas

    def _get_installed_skills(self):
        res_root = self.repo_root / "resources/skills"
        if not res_root.exists(): return []
        return [d for d in os.listdir(res_root) if os.path.isdir(res_root / d)]
