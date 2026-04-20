import os
from pathlib import Path

def get_hermes_home() -> Path:
    """Mock get_hermes_home so we don't need imports that might fail in different context."""
    return Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))

HERMES_HOME = get_hermes_home()
DATA_ROOT = HERMES_HOME / "google_workspace_assistant"
REGISTRY_PATH = DATA_ROOT / "accounts.yaml"
ACCOUNTS_DIR = DATA_ROOT / "accounts"
WORKSPACE_CONFIG_PATH = DATA_ROOT / "workspace_config.yaml"

REQUIRED_PACKAGES = [
    "google-api-python-client",
    "google-auth-oauthlib",
    "google-auth-httplib2",
    "PyYAML",
]

def ensure_dirs():
    """Ensure basic layout exists."""
    ACCOUNTS_DIR.mkdir(parents=True, exist_ok=True)
    if not WORKSPACE_CONFIG_PATH.exists():
        import yaml
        DATA_ROOT.mkdir(parents=True, exist_ok=True)
        default_cfg = {
            "allowed_email_destinations": [
                "javierkijano@gmail.com",
                "javier.gonzalez@metaversetech.es"
            ],
            "mandatory_labels": ["JQASSISTANT"]
        }
        with open(WORKSPACE_CONFIG_PATH, "w") as f:
            yaml.safe_dump(default_cfg, f, sort_keys=False)

def load_workspace_config() -> dict:
    ensure_dirs()
    import yaml
    with open(WORKSPACE_CONFIG_PATH, "r") as f:
        return yaml.safe_load(f) or {}

def ensure_deps():
    """Import time check or helper."""
    pass

def alias_dir(alias: str) -> Path:
    return ACCOUNTS_DIR / alias

def token_path(alias: str) -> Path:
    return alias_dir(alias) / "token.json"

def client_secret_path(alias: str) -> Path:
    return alias_dir(alias) / "client_secret.json"

def pending_auth_path(alias: str) -> Path:
    return alias_dir(alias) / "pending_oauth.json"

import account_registry

def load_registry(path=REGISTRY_PATH) -> dict:
    import yaml
    if not path.exists():
        return {"accounts": {}}
    with open(path, "r") as f:
        return yaml.safe_load(f) or {"accounts": {}}

def save_registry(registry: dict, path=REGISTRY_PATH):
    import yaml
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.safe_dump(registry, f, sort_keys=False)

def get_account(alias: str):
    reg = load_registry(REGISTRY_PATH)
    accounts = reg.get("accounts", {})
    if alias not in accounts:
        return None
    record = accounts[alias]
    from account_registry import AccountRecord
    return AccountRecord(
        alias=alias,
        role=record["role"],
        description=record.get("description", ""),
        services=record.get("services", {})
    )
