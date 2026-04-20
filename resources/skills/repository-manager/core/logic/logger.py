import datetime
import os
import pathlib
import json

def get_runtime_info():
    context = os.environ.get("AGENTIC_CONTEXT", "gemini-cli")
    env = os.environ.get("AGENTIC_ENV", "dev")
    session = os.environ.get("AGENTIC_SESSION", datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    return context, env, session

def get_resource_paths(resource_id):
    # logic/logger.py -> resources/skills/repository-manager/core/logic/logger.py
    core_dir = pathlib.Path(__file__).parent.parent
    res_root = core_dir.parent
    repo_root = res_root.parent.parent.parent
    
    context, env, session = get_runtime_info()
    
    # Path de la sesión en runtime
    session_dir = repo_root / "runtime" / context / env / resource_id / session
    log_dir = session_dir / "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Path del registro de auditoría en runtime
    audit_file = repo_root / "runtime" / context / env / resource_id / "session_registry.jsonl"
    
    # Path del rastro amigable DENTRO de la skill (ignorado por git)
    local_history = res_root / "history.local.md"
    
    return log_dir / f"{resource_id}.log", audit_file, session_dir, local_history

def update_local_history(local_history_path, timestamp, operation, status, session_path):
    header = "# Local Execution History\n\n| Timestamp | Operation | Status | Session Path |\n|-----------|-----------|--------|--------------|\n"
    new_row = f"| {timestamp} | {operation} | {status} | `{session_path}` |\n"
    
    if not os.path.exists(local_history_path):
        with open(local_history_path, "w") as f:
            f.write(header + new_row)
    else:
        with open(local_history_path, "a") as f:
            f.write(new_row)

def log_operation(operation, status, details=""):
    resource_id = "repository-manager"
    log_file, audit_file, session_dir, local_history = get_resource_paths(resource_id)
    
    timestamp = datetime.datetime.now().isoformat()
    
    # 1. Log detallado (Runtime)
    log_entry = f"[{timestamp}] OP: {operation} | STATUS: {status} | DETAILS: {details}\n"
    with open(log_file, "a") as f:
        f.write(log_entry)
    
    # 2. Auditoría JSON (Runtime)
    audit_entry = {
        "timestamp": timestamp,
        "operation": operation,
        "status": status,
        "session_path": str(session_dir),
        "details": details[:100]
    }
    with open(audit_file, "a") as f:
        f.write(json.dumps(audit_entry) + "\n")
        
    # 3. Rastro amigable (Local a la Skill)
    update_local_history(local_history, timestamp, operation, status, session_dir)
