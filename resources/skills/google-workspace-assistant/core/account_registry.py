import yaml
from dataclasses import dataclass
from typing import Literal

ServiceMode = Literal["disabled", "readonly", "readwrite"]
AccountRole = Literal["source", "workspace"]

@dataclass
class AccountRecord:
    alias: str
    role: AccountRole
    description: str
    services: dict[str, ServiceMode]

READONLY_ONLY_SERVICES = {"gmail", "drive", "docs", "sheets", "calendar", "contacts"}

def validate_registry(registry: dict, skip_integrity=False) -> dict:
    accounts = registry.get("accounts") or {}
    workspace_aliases = []
    for alias, record in accounts.items():
        role = record["role"]
        services = record.get("services", {})
        if role == "workspace":
            workspace_aliases.append(alias)
        if role == "source":
            for service, mode in services.items():
                if mode == "readwrite":
                    raise ValueError(f"source account '{alias}' cannot expose readwrite service '{service}'")
    if not skip_integrity and len(workspace_aliases) != 1:
        raise ValueError("v1 requires exactly one workspace account")
    return registry

def load_registry(path) -> dict:
    with open(path, "r") as f:
        registry = yaml.safe_load(f) or {}
    return validate_registry(registry, skip_integrity=True)

def save_registry(registry: dict, path):
    validate_registry(registry, skip_integrity=True)
    with open(path, "w") as f:
        yaml.safe_dump(registry, f, sort_keys=False)

def get_account(registry: dict, alias: str) -> AccountRecord:
    accounts = registry.get("accounts", {})
    if alias not in accounts:
        raise ValueError(f"Account alias '{alias}' not found in registry")
    record = accounts[alias]
    return AccountRecord(
        alias=alias,
        role=record["role"],
        description=record.get("description", ""),
        services=record.get("services", {})
    )

def list_source_aliases(registry: dict) -> list[str]:
    accounts = registry.get("accounts", {})
    return [alias for alias, record in accounts.items() if record["role"] == "source"]

def get_workspace_alias(registry: dict) -> str:
    accounts = registry.get("accounts", {})
    for alias, record in accounts.items():
        if record["role"] == "workspace":
            return alias
    raise ValueError("No workspace account found")

def get_default_source_alias(registry: dict) -> str:
    defaults = registry.get("defaults", {})
    if "default_source_alias" in defaults:
        return defaults["default_source_alias"]
    sources = list_source_aliases(registry)
    if not sources:
        raise ValueError("No source accounts configured")
    return sources[0]
