import argparse
import sys
import json
from pathlib import Path
import assistant_common
import assistant_auth

def get_auth_url(alias: str):
    import google_auth_oauthlib.flow
    
    account = assistant_common.get_account(alias)
    if not account:
        raise ValueError(f"Account alias '{alias}' not found in registry")
        
    client_secret_path = assistant_common.client_secret_path(alias)
    if not client_secret_path.exists():
        raise FileNotFoundError(f"Missing client_secret for '{alias}'. Run: setup.py client-secret --alias {alias} PATH")
        
    scopes = assistant_auth.resolve_scopes(account)
    
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        str(client_secret_path), scopes=scopes
    )
    flow.redirect_uri = "http://localhost:1"
    
    auth_url, state = flow.authorization_url(
        access_type="offline", prompt="consent"
    )
    
    pending_auth_path = assistant_common.pending_auth_path(alias)
    with open(pending_auth_path, "w") as f:
        json.dump({"state": state, "scopes": scopes, "code_verifier": flow.code_verifier}, f)
        
    print(f"Go to this URL to authorize account '{alias}':")
    print(auth_url)
    print(f"\nThen run: setup.py auth-code --alias {alias} <CODE>")

def set_auth_code(alias: str, code: str):
    import google_auth_oauthlib.flow
    import os
    
    pending_auth_path = assistant_common.pending_auth_path(alias)
    if not pending_auth_path.exists():
        raise FileNotFoundError(f"No pending auth state for '{alias}'. Run auth-url first.")
        
    with open(pending_auth_path, "r") as f:
        pending_state = json.load(f)
        
    client_secret_path = assistant_common.client_secret_path(alias)
    scopes = pending_state.get("scopes", [])
    
    # Enable insecure transport for local redirect URIs if needed
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    
    def _extract_code_and_state(code_or_url: str):
        if not code_or_url.startswith("http"):
            return code_or_url, None
        from urllib.parse import parse_qs, urlparse
        parsed = urlparse(code_or_url)
        params = parse_qs(parsed.query)
        return params.get("code", [code_or_url])[0], params.get("state", [None])[0]

    code, returned_state = _extract_code_and_state(code)
    
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        str(client_secret_path), scopes=scopes, state=pending_state.get("state")
    )
    if pending_state.get("code_verifier"):
        flow.code_verifier = pending_state["code_verifier"]
        
    flow.redirect_uri = "http://localhost:1"

    try:
        flow.fetch_token(code=code)
    except Exception as e:
        print(f"Error exchanging code: {e}")
        return
        
    creds = flow.credentials
    token_path = assistant_common.token_path(alias)
    with open(token_path, "w") as f:
        f.write(creds.to_json())
        
    # Clean up pending state
    pending_auth_path.unlink()
    print(f"Authorization complete for '{alias}'.")

def store_client_secret(alias: str, path: str):
    import shutil
    registry = assistant_common.load_registry()
    if alias not in registry.get("accounts", {}):
        raise ValueError(f"Account alias '{alias}' not found in registry")
        
    src = Path(path)
    if not src.exists():
        raise FileNotFoundError(f"Client secret file not found: {path}")
        
    assistant_common.ensure_dirs()
    dst = assistant_common.client_secret_path(alias)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"Stored client secret for '{alias}'")

def add_account(alias: str, role: str, description: str):
    registry = assistant_common.load_registry()
    accounts = registry.get("accounts", {})
    
    if alias in accounts:
        print(f"Account '{alias}' already exists, updating...")
        
    # Set default services based on role
    services = {}
    if role == "source":
        services = {
            "gmail": "readonly",
            "drive": "readonly",
            "docs": "readonly",
            "sheets": "readonly",
            "calendar": "readonly"
        }
    elif role == "workspace":
        services = {
            "gmail": "disabled",
            "drive": "readwrite",
            "docs": "readwrite",
            "sheets": "readwrite",
            "calendar": "disabled"
        }
        
    accounts[alias] = {
        "role": role,
        "description": description,
        "services": services
    }
    
    registry["accounts"] = accounts
    
    from account_registry import validate_registry
    validate_registry(registry, skip_integrity=True)
    
    assistant_common.save_registry(registry)
    
    # Create necessary directories
    alias_dir = assistant_common.alias_dir(alias)
    alias_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Added account '{alias}' ({role})")

def list_accounts():
    registry = assistant_common.load_registry()
    accounts = registry.get("accounts", {})
    
    results = []
    for alias, config in accounts.items():
        has_secret = assistant_common.client_secret_path(alias).exists()
        has_token = assistant_common.token_path(alias).exists()
        
        status = "configured" if has_token else ("pending_auth" if has_secret else "needs_secret")
        # Ensure description is always present to match expectations
        description = config.get("description", "")
        
        results.append({
            "alias": alias,
            "role": config.get("role"),
            "description": description,
            "services": config.get("services", {}),
            "auth_status": status,
            "token_path": str(assistant_common.token_path(alias)) if has_token else None
        })
        
    print(json.dumps(results, indent=2))

def check_account(alias: str):
    account = assistant_common.get_account(alias)
    if not account:
        print(f"Account '{alias}' not found in registry")
        sys.exit(1)
        
    try:
        creds = assistant_auth.get_credentials(alias)
        print(f"Account '{alias}' credentials are VALID.")
        # Try a test API call based on role implicitly by get_credentials validation
    except Exception as e:
        print(f"Account '{alias}' check failed: {e}")

def revoke_account(alias: str):
    import requests
    token_path = assistant_common.token_path(alias)
    if not token_path.exists():
        print(f"No token found for '{alias}'")
        return
        
    payload = assistant_auth.load_token_payload(alias)
    if payload and payload.get("token"):
        # Attempt to revoke token via Google endpoint
        try:
            requests.post("https://oauth2.googleapis.com/revoke", 
                          params={"token": payload["token"]})
            print(f"Revoked token for '{alias}'")
        except Exception as e:
            print(f"Failed to revoke token API: {e}")
            
    token_path.unlink()
    print(f"Removed local credentials for '{alias}'")

def install_deps():
    assistant_common.ensure_deps()
    print("Dependencies are installed.")

def main():
    parser = argparse.ArgumentParser(description="Google Workspace Assistant Setup")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    add_parser = subparsers.add_parser("add-account")
    add_parser.add_argument("--alias", required=True)
    add_parser.add_argument("--role", required=True, choices=["source", "workspace"])
    add_parser.add_argument("--description", default="")
    
    list_parser = subparsers.add_parser("list-accounts")
    
    auth_url_parser = subparsers.add_parser("auth-url")
    auth_url_parser.add_argument("--alias", required=True)
    
    auth_code_parser = subparsers.add_parser("auth-code")
    auth_code_parser.add_argument("--alias", required=True)
    auth_code_parser.add_argument("code")
    
    client_secret_parser = subparsers.add_parser("client-secret")
    client_secret_parser.add_argument("--alias", required=True)
    client_secret_parser.add_argument("path")
    
    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--alias", required=True)
    
    revoke_parser = subparsers.add_parser("revoke")
    revoke_parser.add_argument("--alias", required=True)
    
    install_parser = subparsers.add_parser("install-deps")

    args = parser.parse_args()

    try:
        if args.command == "add-account":
            add_account(args.alias, args.role, args.description)
        elif args.command == "list-accounts":
            list_accounts()
        elif args.command == "auth-url":
            get_auth_url(args.alias)
        elif args.command == "auth-code":
            set_auth_code(args.alias, args.code)
        elif args.command == "client-secret":
            store_client_secret(args.alias, args.path)
        elif args.command == "check":
            check_account(args.alias)
        elif args.command == "revoke":
            revoke_account(args.alias)
        elif args.command == "install-deps":
            install_deps()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
