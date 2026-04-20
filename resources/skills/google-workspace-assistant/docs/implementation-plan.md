# Google Workspace Assistant Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build a dedicated `google-workspace-assistant` skill that can read from multiple human-owned Google source accounts in read-only mode and write only into one assistant-owned workspace account.

**Architecture:** Keep the original `google-workspace` skill untouched. Implement a new assistant-specific runtime with an explicit account registry, fixed roles (`source` vs `workspace`), per-account credential bundles, deterministic routing, and no code path that permits writes against any source account. The assistant should inspect real inbox/thread context from named source aliases while storing summaries, drafts, trackers, and working artifacts exclusively in the workspace account.

**Tech Stack:** Python 3.11, `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`, YAML/JSON config under `~/.hermes`, pytest in `/home/jq-hermes-01/.hermes/hermes-agent/tests/skills`, existing Hermes skill layout under `~/.hermes/skills`.

---

## Requirements Recap

This plan implements the product the user actually wants:

1. The original `google-workspace` skill must remain conceptually clean and separate.
2. A new skill, `google-workspace-assistant`, must support multiple read-only source accounts.
3. There should be one canonical writable assistant workspace account in v1.
4. The assistant must be able to inspect the real inbox/thread context of each source account.
5. The assistant must never write into source accounts through this skill.
6. The assistant should write notes, summaries, draft docs, and trackers into its own Google account.
7. Gmail send must be disabled in v1, even for the workspace account.
8. The runtime should route by role and alias, not by free-form profile switching.

## Acceptance Criteria

The implementation is complete only when all of these are true:

- `google-workspace-assistant` has its own scripts and docs under `/home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/`.
- The skill supports at least 3 named source aliases without code changes.
- Source aliases are limited to readonly scopes for enabled services.
- The workspace alias is the only writable account.
- Parser/runtime make source writes impossible, not merely discouraged in docs.
- No `gmail send`, `gmail reply`, or `gmail modify` path exists in v1.
- The skill can read Gmail from a named source alias and create/update Docs and Sheets in the workspace account.
- Tests cover registry validation, alias-specific auth paths, source readonly routing, workspace write routing, and absence of Gmail send commands.

## Current Codebase Facts To Reuse

Use these existing files as source material only; do not rename them into the new product:

- `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace/scripts/setup.py`
- `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace/scripts/google_api.py`
- `/home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_oauth_setup.py`
- `/home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_api.py`

Relevant observations from the current implementation:

1. `google_api.py` is single-account and hardcodes one `TOKEN_PATH` plus one `SCOPES` list.
2. `setup.py` is single-account and hardcodes one `CLIENT_SECRET_PATH`, one `TOKEN_PATH`, and one `PENDING_AUTH_PATH`.
3. Gmail read and write commands are mixed into the same parser.
4. Drive is currently read-only; Docs is read-only; Sheets already supports write.
5. Existing tests already show the preferred style for fake credentials and fake OAuth flows.

## Final File Layout To Build

### Skill files

- Modify: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/SKILL.md`
- Modify: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/references/architecture.md`
- Modify: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/references/accounts-example.yaml`
- Create: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/references/implementation-plan.md`
- Create: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/scripts/assistant_common.py`
- Create: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/scripts/account_registry.py`
- Create: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/scripts/assistant_auth.py`
- Create: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/scripts/setup.py`
- Create: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/scripts/google_api.py`

### Data files under HERMES_HOME

Use a dedicated namespaced root instead of reusing the original skill’s flat files:

- Create at runtime: `~/.hermes/google_workspace_assistant/accounts.yaml`
- Create at runtime: `~/.hermes/google_workspace_assistant/accounts/<alias>/client_secret.json`
- Create at runtime: `~/.hermes/google_workspace_assistant/accounts/<alias>/token.json`
- Create at runtime: `~/.hermes/google_workspace_assistant/accounts/<alias>/pending_oauth.json`

### Tests

- Create: `/home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_registry.py`
- Create: `/home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_setup.py`
- Create: `/home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_api.py`

---

## Task 1: Freeze the runtime contract and storage layout

**Objective:** Make the skill’s role model, on-disk structure, and CLI shape explicit before any code is written.

**Files:**
- Modify: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/SKILL.md`
- Modify: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/references/architecture.md`
- Modify: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/references/accounts-example.yaml`
- Create: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/references/implementation-plan.md`

**Step 1: Update the architecture docs to use one concrete storage root**

Use this convention everywhere:

```python
DATA_ROOT = get_hermes_home() / "google_workspace_assistant"
REGISTRY_PATH = DATA_ROOT / "accounts.yaml"
ACCOUNTS_DIR = DATA_ROOT / "accounts"
```

This replaces any vague example like `google_accounts/...` with one feature-specific home.

**Step 2: Lock the CLI contract in docs**

Document these commands as the target interface:

```bash
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py add-account --alias personal --role source
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py add-account --alias metabestec --role source
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py add-account --alias assistant --role workspace
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py auth-url --alias personal
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py auth-code --alias personal "http://localhost:1/?code=..."
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py list-accounts
```

```bash
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/google_api.py source personal gmail search "is:unread"
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/google_api.py source metabestec gmail get MESSAGE_ID
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/google_api.py workspace docs create --title "Draft response" --body "..."
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/google_api.py workspace sheets append SHEET_ID "Inbox!A:D" --values '[["ts","source","subject","summary"]]'
```

**Step 3: Define the registry schema**

Use this model as the source of truth:

```python
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
```

**Step 4: Verification**

Manual check only at this stage:
- `SKILL.md` explains source/workspace asymmetry.
- The architecture doc uses `~/.hermes/google_workspace_assistant/...` consistently.
- `accounts-example.yaml` shows at least `personal`, `metabestec`, and `assistant`.

**Step 5: Commit**

```bash
git add docs/plans/2026-04-06-google-workspace-assistant-implementation-plan.md
# plus any updated skill docs if mirrored in repo
# git commit -m "docs: freeze google workspace assistant contract"
```

---

## Task 2: Build shared path/bootstrap helpers

**Objective:** Centralize path resolution, dependency checks, and script-local imports so setup and runtime code do not duplicate fragile logic.

**Files:**
- Create: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/scripts/assistant_common.py`
- Test: `/home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_registry.py`

**Step 1: Write failing tests for path helpers**

```python
def test_data_root_is_namespaced(monkeypatch, tmp_path):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    module = load_module("assistant_common.py")
    assert module.DATA_ROOT == tmp_path / "google_workspace_assistant"
    assert module.REGISTRY_PATH == tmp_path / "google_workspace_assistant" / "accounts.yaml"
```

**Step 2: Implement minimal helper module**

```python
from pathlib import Path
from hermes_constants import get_hermes_home

HERMES_HOME = get_hermes_home()
DATA_ROOT = HERMES_HOME / "google_workspace_assistant"
REGISTRY_PATH = DATA_ROOT / "accounts.yaml"
ACCOUNTS_DIR = DATA_ROOT / "accounts"
REQUIRED_PACKAGES = [
    "google-api-python-client",
    "google-auth-oauthlib",
    "google-auth-httplib2",
    "PyYAML",
]
```

Also add helper functions:
- `ensure_dirs()`
- `ensure_deps()`
- `alias_dir(alias)`
- `token_path(alias)`
- `client_secret_path(alias)`
- `pending_auth_path(alias)`

**Step 3: Run the test**

Run:
```bash
pytest /home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_registry.py -q
```
Expected: one new path-helper test passes or, if the file is not implemented yet, fails on import until fixed.

**Step 4: Commit**

```bash
git add /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/assistant_common.py         /home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_registry.py
# git commit -m "feat: add shared helpers for google workspace assistant"
```

---

## Task 3: Implement registry loading, validation, and role invariants

**Objective:** Make account definitions explicit and reject unsafe configurations before OAuth or API calls happen.

**Files:**
- Create: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/scripts/account_registry.py`
- Modify: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/references/accounts-example.yaml`
- Test: `/home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_registry.py`

**Step 1: Write failing tests for registry invariants**

```python
def test_rejects_source_account_with_readwrite_service(tmp_path):
    cfg = {
        "accounts": {
            "personal": {
                "role": "source",
                "description": "Main inbox",
                "services": {"gmail": "readwrite"},
            }
        }
    }
    with pytest.raises(ValueError, match="source.*readonly"):
        load_registry_dict(cfg)


def test_requires_exactly_one_workspace_in_v1(tmp_path):
    cfg = {"accounts": {}}
    with pytest.raises(ValueError, match="workspace"):
        load_registry_dict(cfg)
```

**Step 2: Implement the validator**

```python
READONLY_ONLY_SERVICES = {"gmail", "drive", "docs", "sheets", "calendar", "contacts"}


def validate_registry(registry: dict) -> dict:
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
    if len(workspace_aliases) != 1:
        raise ValueError("v1 requires exactly one workspace account")
    return registry
```

**Step 3: Add accessor helpers**

Required helpers:
- `load_registry()`
- `save_registry()`
- `get_account(alias)`
- `list_source_aliases()`
- `get_workspace_alias()`
- `get_default_source_alias()`

**Step 4: Run tests**

Run:
```bash
pytest /home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_registry.py -q
```
Expected: registry validation tests pass.

**Step 5: Commit**

```bash
git add /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/account_registry.py         /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/references/accounts-example.yaml         /home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_registry.py
# git commit -m "feat: add registry and role validation for google workspace assistant"
```

---

## Task 4: Implement role-aware scope resolution and credential loading

**Objective:** Compute minimal OAuth scopes per alias and ensure each command loads the correct token bundle.

**Files:**
- Create: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/scripts/assistant_auth.py`
- Test: `/home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_setup.py`
- Test: `/home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_api.py`

**Step 1: Write failing tests for scope resolution**

```python
def test_source_gmail_scope_is_readonly_only(module):
    account = AccountRecord(
        alias="personal",
        role="source",
        description="",
        services={"gmail": "readonly"},
    )
    assert resolve_scopes(account) == ["https://www.googleapis.com/auth/gmail.readonly"]


def test_workspace_docs_and_sheets_scopes_are_writable(module):
    account = AccountRecord(
        alias="assistant",
        role="workspace",
        description="",
        services={"docs": "readwrite", "sheets": "readwrite"},
    )
    assert "https://www.googleapis.com/auth/documents" in resolve_scopes(account)
    assert "https://www.googleapis.com/auth/spreadsheets" in resolve_scopes(account)
```

**Step 2: Implement scope maps**

```python
SERVICE_SCOPE_MAP = {
    "gmail": {"readonly": ["https://www.googleapis.com/auth/gmail.readonly"]},
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
```

**Step 3: Implement credential helpers**

Required helpers:
- `resolve_scopes(account_record)`
- `load_token_payload(alias)`
- `missing_scopes(alias)`
- `get_credentials(alias)`
- `build_service(alias, api, version)`

Critical behavior:
- `get_credentials("personal")` must only validate the scopes needed by `personal`.
- `get_credentials("assistant")` must validate only the workspace account’s enabled services.
- Missing scopes must mention the alias in the error output.

**Step 4: Run tests**

Run:
```bash
pytest /home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_setup.py -q
pytest /home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_api.py -q
```
Expected: scope-resolution and alias-specific token tests fail first, then pass.

**Step 5: Commit**

```bash
git add /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/assistant_auth.py         /home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_setup.py         /home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_api.py
# git commit -m "feat: add role-aware scopes and credential loading"
```

---

## Task 5: Implement the multi-account setup CLI

**Objective:** Let the user register aliases, store per-alias client secrets, run alias-specific OAuth, and inspect the configured topology.

**Files:**
- Create: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/scripts/setup.py`
- Reuse: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/scripts/assistant_common.py`
- Reuse: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/scripts/account_registry.py`
- Reuse: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/scripts/assistant_auth.py`
- Test: `/home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_setup.py`

**Step 1: Write failing tests for alias-specific setup behavior**

```python
def test_add_account_writes_registry_entry(setup_module, tmp_path):
    setup_module.add_account(alias="personal", role="source", description="Main inbox")
    saved = load_yaml(tmp_path / "google_workspace_assistant" / "accounts.yaml")
    assert saved["accounts"]["personal"]["role"] == "source"


def test_auth_url_persists_pending_state_inside_alias_dir(setup_module):
    setup_module.add_account(alias="personal", role="source", description="Main inbox")
    setup_module.store_client_secret(alias="personal", path="/tmp/client_secret.json")
    setup_module.get_auth_url(alias="personal")
    assert (setup_module.DATA_ROOT / "accounts" / "personal" / "pending_oauth.json").exists()
```

**Step 2: Implement setup subcommands**

Required subcommands:
- `add-account --alias --role --description`
- `remove-account --alias`
- `list-accounts`
- `show-account --alias`
- `client-secret --alias PATH`
- `auth-url --alias`
- `auth-code --alias CODE_OR_URL`
- `check --alias`
- `revoke --alias`
- `install-deps`

**Step 3: Reuse the current headless PKCE flow**

Copy the good parts of the current single-account setup flow, but make every path alias-specific:

```python
alias_root = ACCOUNTS_DIR / alias
client_secret_path = alias_root / "client_secret.json"
token_path = alias_root / "token.json"
pending_auth_path = alias_root / "pending_oauth.json"
```

**Step 4: Add machine-readable `list-accounts` output**

Print JSON by default. Each record should include:
- alias
- role
- description
- enabled services
- auth status
- token path

**Step 5: Run tests**

Run:
```bash
pytest /home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_setup.py -q
```
Expected: setup tests pass for add/list/check/auth-url/auth-code/revoke behavior.

**Step 6: Commit**

```bash
git add /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py         /home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_setup.py
# git commit -m "feat: add multi-account setup cli for google workspace assistant"
```

---

## Task 6: Implement source-account readonly runtime commands

**Objective:** Read real inbox and document context from named source aliases without exposing any write path.

**Files:**
- Create: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/scripts/google_api.py`
- Reuse: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/scripts/assistant_auth.py`
- Test: `/home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_api.py`

**Step 1: Write failing tests for source routing**

```python
def test_source_gmail_search_uses_named_alias(api_module):
    api_module.gmail_search(make_args(source_alias="personal", query="is:unread", max=10))
    assert api_module._last_service_request == ("personal", "gmail", "v1")


def test_source_docs_get_uses_named_alias(api_module):
    api_module.docs_get(make_args(source_alias="metabestec", doc_id="doc-123"))
    assert api_module._last_service_request == ("metabestec", "docs", "v1")
```

**Step 2: Implement only readonly source commands**

Source role must expose these commands in v1:
- `source <alias> gmail search QUERY`
- `source <alias> gmail get MESSAGE_ID`
- `source <alias> drive search QUERY`
- `source <alias> docs get DOC_ID`
- `source <alias> sheets get SHEET_ID RANGE`
- `source <alias> calendar list [--start --end]`
- `source <alias> contacts list`

Do **not** port or expose any source write command.

**Step 3: Reuse the existing read implementations where possible**

Port logic from the original skill for:
- Gmail search/get
- Drive search
- Contacts list
- Sheets get
- Docs get
- Calendar list

But change every service builder call to:

```python
service = build_service(alias, "gmail", "v1")
```

instead of hardcoded single-account `build_service("gmail", "v1")`.

**Step 4: Run tests**

Run:
```bash
pytest /home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_api.py -q
```
Expected: source read commands pass and resolve the right alias.

**Step 5: Commit**

```bash
git add /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/google_api.py         /home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_api.py
# git commit -m "feat: add readonly source-account api commands"
```

---

## Task 7: Implement workspace-account write commands

**Objective:** Give the assistant a productive writable sandbox without reintroducing email sending.

**Files:**
- Modify: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/scripts/google_api.py`
- Modify: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/references/accounts-example.yaml`
- Test: `/home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_api.py`

**Step 1: Write failing tests for workspace-only writes**

```python
def test_workspace_docs_create_uses_default_workspace_alias(api_module):
    api_module.docs_create(make_args(title="Draft", body="Hello"))
    assert api_module._last_service_request == ("assistant", "docs", "v1")


def test_workspace_sheets_append_uses_default_workspace_alias(api_module):
    api_module.sheets_append(make_args(sheet_id="sheet-1", range="Inbox!A:D", values='[["x"]]'))
    assert api_module._last_service_request == ("assistant", "sheets", "v4")
```

**Step 2: Implement the minimum writable surface**

Required v1 workspace commands:
- `workspace docs create --title --body`
- `workspace docs append DOC_ID --text`
- `workspace sheets update SHEET_ID RANGE --values JSON`
- `workspace sheets append SHEET_ID RANGE --values JSON`
- `workspace drive search QUERY`

Recommended docs create/append implementation:

```python
def docs_create(args):
    service = build_service(get_workspace_alias(), "docs", "v1")
    doc = service.documents().create(body={"title": args.title}).execute()
    if args.body:
        service.documents().batchUpdate(
            documentId=doc["documentId"],
            body={"requests": [{"insertText": {"location": {"index": 1}, "text": args.body}}]},
        ).execute()
    print(json.dumps({"documentId": doc["documentId"], "title": args.title}, indent=2))
```

**Step 3: Explicitly keep Gmail disabled in workspace v1**

Do not implement:
- `workspace gmail send`
- `workspace gmail reply`
- `workspace gmail modify`

The parser should have no such subcommands.

**Step 4: Run tests**

Run:
```bash
pytest /home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_api.py -q
```
Expected: workspace write tests pass; no Gmail write command exists.

**Step 5: Commit**

```bash
git add /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/google_api.py         /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/references/accounts-example.yaml         /home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_api.py
# git commit -m "feat: add workspace write commands without gmail send"
```

---

## Task 8: Enforce parser-level safety and impossible source writes

**Objective:** Make unsafe operations structurally impossible through CLI shape and route checks.

**Files:**
- Modify: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/scripts/google_api.py`
- Test: `/home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_api.py`

**Step 1: Write failing safety tests**

```python
def test_parser_has_no_source_write_commands(api_module):
    parser = api_module.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["source", "personal", "gmail", "send"])


def test_parser_has_no_workspace_gmail_send_command(api_module):
    parser = api_module.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["workspace", "gmail", "send"])
```

**Step 2: Refactor parser creation into a testable function**

```python
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(...)
    roles = parser.add_subparsers(dest="role", required=True)
    # add source tree
    # add workspace tree
    return parser
```

**Step 3: Add runtime guards even though the parser already restricts commands**

```python
def assert_source_readonly(account):
    if account.role != "source":
        raise ValueError("expected source account")


def assert_workspace_write_enabled(account, service):
    if account.role != "workspace":
        raise ValueError("writes require workspace account")
```

This is defense in depth: parser restriction first, runtime assertion second.

**Step 4: Run tests**

Run:
```bash
pytest /home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_api.py -q
```
Expected: tests prove unsafe commands are absent.

**Step 5: Commit**

```bash
git add /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/google_api.py         /home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_api.py
# git commit -m "feat: harden parser and forbid source writes"
```

---

## Task 9: Update docs and usage examples for real operator workflows

**Objective:** Make the skill usable by future-you without rereading this chat.

**Files:**
- Modify: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/SKILL.md`
- Modify: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/references/architecture.md`
- Modify: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/references/accounts-example.yaml`
- Create: `/home/jq-hermes-01/.hermes/skills/productivity/google-workspace-assistant/references/implementation-plan.md`

**Step 1: Document the happy path**

Add a setup walkthrough with these exact steps:

```bash
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py add-account --alias personal --role source --description "Cuenta personal principal"
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py add-account --alias metabestec --role source --description "Inbox operativo de Metabestec"
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py add-account --alias assistant --role workspace --description "Sandbox del asistente"
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py auth-url --alias personal
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py auth-url --alias metabestec
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py auth-url --alias assistant
```

**Step 2: Document the safe runtime examples**

```bash
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/google_api.py source personal gmail search "label:inbox newer_than:2d"
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/google_api.py source metabestec gmail search "is:unread"
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/google_api.py workspace docs create --title "Resumen diario" --body "..."
```

**Step 3: Add a clear warning block**

The docs must say:
- source accounts are read-only by design
- workspace Gmail send is intentionally disabled in v1
- forwarding is not required because source accounts are inspected directly

**Step 4: Verification**

Manual doc review only:
- A future operator can see how to add multiple source accounts.
- The examples never show source writes.
- The examples never show Gmail send.

**Step 5: Commit**

```bash
git add /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/SKILL.md         /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/references/architecture.md         /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/references/accounts-example.yaml         /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/references/implementation-plan.md
# git commit -m "docs: document google workspace assistant workflows"
```

---

## Task 10: Run end-to-end verification with three aliases

**Objective:** Prove the full topology works for the concrete case the user described.

**Files:**
- No new source files required; use the completed implementation and docs.

**Step 1: Configure three aliases**

Target registry:

```yaml
accounts:
  personal:
    role: source
    description: Cuenta personal principal
    services:
      gmail: readonly
      drive: readonly
      docs: readonly
      sheets: readonly
      calendar: readonly
  metabestec:
    role: source
    description: Cuenta operativa de Metabestec
    services:
      gmail: readonly
      drive: readonly
      docs: readonly
      sheets: readonly
      calendar: readonly
  assistant:
    role: workspace
    description: Sandbox del asistente
    services:
      gmail: disabled
      drive: readwrite
      docs: readwrite
      sheets: readwrite
      calendar: disabled
```

**Step 2: Verify each alias auth state**

Run:
```bash
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py list-accounts
```
Expected: JSON shows `personal`, `metabestec`, and `assistant`, with explicit auth status.

**Step 3: Verify source Gmail reads**

Run:
```bash
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/google_api.py source personal gmail search "newer_than:7d"
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/google_api.py source metabestec gmail search "is:unread"
```
Expected: both commands succeed and clearly hit different aliases.

**Step 4: Verify workspace writes**

Run:
```bash
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/google_api.py workspace docs create --title "Prueba workspace" --body "El asistente escribe aquí."
```
Expected: document is created in the assistant account, not in either source account.

**Step 5: Verify forbidden behavior**

Run these and expect failure:

```bash
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/google_api.py source personal gmail send --to x@example.com --subject nope --body nope
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/google_api.py workspace gmail send --to x@example.com --subject nope --body nope
```

Expected: parser error or explicit unsupported-command failure.

---

## Test Matrix Summary

Run the full suite with:

```bash
pytest /home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_registry.py -q
pytest /home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_setup.py -q
pytest /home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_api.py -q
```

Then run everything together:

```bash
pytest /home/jq-hermes-01/.hermes/hermes-agent/tests/skills/test_google_workspace_assistant_*.py -q
```

## Deliberately Out Of Scope For V1

Do not add these in the first implementation:

- external email sending from source or workspace
- Gmail reply from the assistant account
- arbitrary multi-workspace support
- source account write exceptions
- generic `--profile` switching
- write-capable Drive file deletion APIs
- background synchronization between accounts

## Notes For The Implementer

1. Prefer copying the good test patterns from the existing Google Workspace tests rather than inventing a new style.
2. Keep parser shape simple and impossible to misuse.
3. If a design choice feels “more flexible” but weakens routing safety, reject it.
4. If Docs write support becomes noisy, ship only `docs create` and `docs append` in v1.
5. If Drive write support is not strictly needed for the user’s first workflow, defer it and rely on Docs/Sheets writes first.
6. Treat source read-only guarantees as product invariants, not suggestions.

## Implementation Order Recommendation

Do the work in this exact order:

1. docs + storage root
2. helper module
3. registry + validation
4. scopes + auth
5. setup CLI
6. source readonly commands
7. workspace write commands
8. parser hardening
9. docs refresh
10. end-to-end verification

## Ready-To-Execute Handoff

Plan complete and saved. Ready to execute using subagent-driven-development — one task at a time, with spec-compliance review and then code-quality review after each task.
