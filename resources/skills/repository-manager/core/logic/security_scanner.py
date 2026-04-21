import re
import os
import pathlib

class SecurityScanner:
    def __init__(self, repo_root):
        self.repo_root = pathlib.Path(repo_root)
        # Patrones comunes de secretos e información sensible
        self.patterns = {
            "API Key / Secret": r"(?i)(api_key|secret|password|passwd|auth_token|access_key)[\s:=]+['\"]([a-zA-Z0-9_\-]{16,})['\"]",
            "Generic Token": r"[a-fA-F0-9]{32,}",
            "Private Key": r"-----BEGIN (RSA|OPENSSH|PRIVATE) KEY-----",
            "Email Address": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            "Google OAuth": r"client_id\": \"[0-9-]+-[a-z0-9.]+\.apps\.googleusercontent\.com\"",
        }
        
        # Extensiones a ignorar (binarios, etc)
        self.ignored_exts = {'.pyc', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.bin'}
        # Directorios a ignorar (donde SÍ puede haber secretos, pero están en el .gitignore)
        self.ignored_dirs = {'runtime', '.git', 'dist', '__pycache__'}

    def scan_file(self, file_path):
        findings = []
        try:
            content = file_path.read_text(errors='ignore')
            for name, pattern in self.patterns.items():
                matches = re.finditer(pattern, content)
                for match in matches:
                    # Capturamos la línea para dar contexto
                    line_no = content.count('\n', 0, match.start()) + 1
                    # Censuramos el valor real en el reporte por seguridad
                    val = match.group(0)
                    
                    if name == "Email Address" and (val.endswith("@example.com") or val.endswith("@test.com")):
                        continue
                    if name == "Generic Token":
                        ctx_start = max(0, match.start() - 100)
                        if "http" in content[ctx_start:match.start()]:
                            continue

                    safe_val = val[:10] + "..." + val[-5:] if len(val) > 15 else "***"
                    findings.append({
                        "type": name,
                        "file": str(file_path.relative_to(self.repo_root)),
                        "line": line_no,
                        "finding": safe_val
                    })
        except Exception as e:
            pass # Ignorar archivos no legibles
        return findings

    def run_full_scan(self):
        all_findings = []
        for root, dirs, files in os.walk(self.repo_root):
            # Filtrar directorios ignorados
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
            
            for file in files:
                f_path = pathlib.Path(root) / file
                if f_path.suffix.lower() in self.ignored_exts:
                    continue
                
                all_findings.extend(self.scan_file(f_path))
        
        return all_findings
