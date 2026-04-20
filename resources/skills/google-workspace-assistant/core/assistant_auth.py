from dataclasses import dataclass
from typing import Literal, List, Dict
import os
import json
import assistant_common

ServiceMode = Literal["disabled", "readonly", "readwrite"]
AccountRole = Literal["source", "workspace"]

@dataclass
class AccountRecord:
    alias: str
    role: AccountRole
    description: str
    services: dict[str, ServiceMode]

SERVICE_SCOPE_MAP = {
    "gmail": {
        "readonly": ["https://www.googleapis.com/auth/gmail.readonly"],
        "readwrite": [
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.modify"
        ]
    },
    "drive": {
        "readonly": ["https://www.googleapis.com/auth/drive.readonly"],
        "readwrite": ["https://www.googleapis.com/auth/drive.file"],
    },
    "docs": {
        "readonly": ["https://www.googleapis.com/auth/documents.readonly"],
        "readwrite": ["https://www.googleapis.com/auth/documents"],
    },
    "sheets": {
        "readonly": ["https://www.googleapis.com/auth/spreadsheets.readonly"],
        "readwrite": ["https://www.googleapis.com/auth/spreadsheets"],
    },
    "calendar": {
        "readonly": ["https://www.googleapis.com/auth/calendar.readonly"],
        "readwrite": ["https://www.googleapis.com/auth/calendar"],
    },
    "contacts": {
        "readonly": ["https://www.googleapis.com/auth/contacts.readonly"],
    },
}

def resolve_scopes(account: AccountRecord) -> list[str]:
    scopes = []
    for service, mode in account.services.items():
        if mode == "disabled":
            continue
        if service in SERVICE_SCOPE_MAP and mode in SERVICE_SCOPE_MAP[service]:
            scopes.extend(SERVICE_SCOPE_MAP[service][mode])
    return list(set(scopes))


def load_token_payload(alias: str) -> dict | None:
    token_path = assistant_common.ACCOUNTS_DIR / alias / "token.json"
    if not token_path.exists():
        return None
    try:
        with open(token_path, "r") as f:
            return json.load(f)
    except Exception:
        return None


def missing_scopes(alias: str, required_scopes: list[str]) -> list[str]:
    payload = load_token_payload(alias)
    if not payload:
        return required_scopes
    
    granted_scopes = payload.get("scopes", [])
    # Handle both single string and list formats
    if isinstance(granted_scopes, str):
        granted_scopes = granted_scopes.split()
        
    return [s for s in required_scopes if s not in granted_scopes]


def get_credentials(alias: str):
    from google.oauth2.credentials import Credentials
    import account_registry
    import assistant_common
    reg = assistant_common.load_registry()
    account = account_registry.get_account(reg, alias)
    if not account:
        raise ValueError(f"Account alias '{alias}' not found in registry")
        
    required_scopes = resolve_scopes(account)
    
    token_path = assistant_common.ACCOUNTS_DIR / alias / "token.json"
    if not token_path.exists():
        raise FileNotFoundError(f"Missing token for '{alias}'. Run: setup.py auth-url --alias {alias}")
        
    creds = Credentials.from_authorized_user_file(str(token_path), required_scopes)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            # Save the refreshed credentials
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        else:
            raise ValueError(f"Invalid or expired credentials for '{alias}'")
            
    # Check for missing scopes after token is loaded/refreshed
    missing = missing_scopes(alias, required_scopes)
    if missing:
        raise ValueError(f"Token for '{alias}' is missing required scopes: {missing}. Run auth-url again.")
        
    return creds

def build_service(alias: str, service_name: str, version: str):
    from googleapiclient.discovery import build
    creds = get_credentials(alias)
    return build(service_name, version, credentials=creds)
