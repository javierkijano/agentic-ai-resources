# Repository Change Workflows

This document defines the mandatory steps for different types of modifications within the Agentic Resources repository.

## Change Types & Requirements

### 1. NEW_RESOURCE (Creating a skill, agent, or pack)
- [ ] **Scaffold**: Use `scripts/create_resource.py`.
- [ ] **Metadata**: Complete all mandatory fields in `resource.yaml`.
- [ ] **Contract**: Create `core/docs/STORAGE.md` and `core/docs/TODOs.md`.
- [ ] **Standard Logic**: Implement core functionality in `core/logic/`.
- [ ] **Validation**: Run `scripts/validate_repo.py`.

### 2. LOGIC_UPDATE (Modifying existing functionality)
- [ ] **Research**: Read `resource.yaml` and `STORAGE.md` to understand side effects.
- [ ] **Testing**: Create or update a test in the `tests/` directory of the resource.
- [ ] **Verification**: Run the specific test and then `scripts/validate_repo.py`.
- [ ] **History**: Log the change in the resource's `history.local.md`.

### 3. CROSS_CUTTING (Changes affecting 'shared/' or 'scripts/')
- [ ] **Impact Analysis**: Identify all resources that depend on the modified shared component.
- [ ] **Regression Testing**: Run tests for at least 2 dependent resources.
- [ ] **Infrastructure**: If a script changes, verify it works for both `hermes` and `generic` platforms.
- [ ] **Validation**: Full `scripts/validate_repo.py`.

### 4. SECURITY_FIX (Removing secrets or PII)
- [ ] **Pre-flight**: Identify potential leaks locally before running full validation (e.g., searching for known email domains or keys).
- [ ] **Detection**: Run `scripts/validate_repo.py` to confirm the finding.
- [ ] **Redaction**: Remove/Replace the sensitive data.
- [ ] **Verification**: Re-run validation to ensure the scan passes.
- [ ] **Root Cause**: If the secret was in a config, ensure `resource.yaml` defines it as a credential requirement instead of hardcoding it.

### 5. PLATFORM_OVERLAY (Adding support for Hermes, Albert, etc.)
- [ ] **Structure**: Create `platforms/{{platform_id}}/`.
- [ ] **Consistency**: Ensure the overlay matches the `core/` logic interface.
- [ ] **Build**: Run `scripts/build_platform.py --platform {{platform_id}}`.
- [ ] **Artifact Check**: Inspect the `dist/` output for the specific platform.

## Usage Protocol
Agents should call `repository-manager` to get the specific checklist for their task before committing any changes.
