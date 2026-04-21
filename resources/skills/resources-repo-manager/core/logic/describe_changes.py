#!/usr/bin/env python3
import subprocess
import os
import sys
import pathlib
from security_scanner import SecurityScanner

def get_git_status():
    try:
        # Get staged changes
        staged = subprocess.check_output(['git', 'diff', '--cached', '--name-status']).decode('utf-8').splitlines()
        return staged
    except Exception as e:
        print(f"ERROR: Could not get git status: {e}")
        return []

def group_changes(staged_files):
    summary = {
        "skills": set(),
        "knowledge": set(),
        "scripts": set(),
        "docs": set(),
        "others": []
    }
    
    for line in staged_files:
        if not line: continue
        status, path = line.split(None, 1)
        
        if path.startswith('resources/skills/'):
            skill_id = path.split('/')[2]
            summary["skills"].add(f"{status}: {skill_id}")
        elif path.startswith('resources/knowledge-packs/'):
            kp_id = path.split('/')[2]
            summary["knowledge"].add(f"{kp_id}")
        elif path.startswith('scripts/'):
            summary["scripts"].add(os.path.basename(path))
        elif path.startswith('docs/'):
            summary["docs"].add(os.path.basename(path))
        else:
            summary["others"].append(f"{status}: {path}")
            
    return summary

def format_commit_message(summary):
    lines = []
    lines.append("feat: integrate and update agentic resources")
    lines.append("")
    
    if summary["skills"]:
        lines.append("Skills:")
        for s in sorted(summary["skills"]):
            lines.append(f"  - {s}")
            
    if summary["knowledge"]:
        lines.append("Knowledge Packs:")
        for k in sorted(summary["knowledge"]):
            lines.append(f"  - {k}")
            
    if summary["scripts"] or summary["docs"]:
        lines.append("Core Infrastructure:")
        for s in sorted(summary["scripts"]):
            lines.append(f"  - script: {s}")
        for d in sorted(summary["docs"]):
            lines.append(f"  - doc: {d}")
            
    if summary["others"]:
        lines.append("Other Changes:")
        for o in summary["others"]:
            lines.append(f"  - {o}")
            
    return "\n".join(lines)

if __name__ == "__main__":
    staged = get_git_status()
    if not staged:
        print("No staged changes found. Use 'git add' first.")
        sys.exit(0)
        
    # Security Check before generating message
    repo_root = pathlib.Path(__file__).parent.parent.parent.parent.parent
    scanner = SecurityScanner(repo_root)
    findings = []
    
    # Solo escaneamos los archivos en el staging
    for line in staged:
        if not line: continue
        parts = line.split(None, 1)
        if len(parts) < 2: continue
        status, path = parts
        if status != 'D': # No escanear borrados
            f_path = repo_root / path
            if f_path.exists():
                findings.extend(scanner.scan_file(f_path))

    if findings:
        print("\n" + "!"*60)
        print("CRITICAL SECURITY WARNING: POTENTIAL SECRETS DETECTED IN STAGING")
        print("!"*60)
        for f in findings:
            print(f"  [!] {f['type']} in {f['file']}:{f['line']}")
        
        print("\n[SECURITY BLOCK] Please remove secrets before committing.")
        print("If you are ABSOLUTELY sure, use 'git commit' directly to bypass this tool.")
        sys.exit(2)

    summary = group_changes(staged)
    print("\n--- Suggested Commit Message ---")
    print("--------------------------------")
    print(format_commit_message(summary))
    print("--------------------------------")
