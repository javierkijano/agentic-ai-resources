# Conventions

Standardizing the structure and metadata of resources ensures they are portable and easy to manage.

## Resource Pack Structure

Each resource in `resources/<type>/<id>/` should follow this general layout:

```
<id>/
  resource.yaml    # Mandatory metadata
  README.md        # Documentation for the resource
  core/
    logic/         # Reusable business logic
    cli/           # CLI entrypoints and command definitions
    webapp/        # Web-based management interface
    infra/         # Infrastructure files (Dockerfile, requirements.txt, etc.)
    docs/          # Internal documentation (STORAGE.md, CREDENTIALS.md, TODOs.md)
  platforms/       # Platform-specific overlays (e.g., platforms/hermes/SKILL.md)
```

## `resource.yaml` Schema

Every resource must include a `resource.yaml` with at least the following fields:

- `id`: Unique identifier (e.g., `git-helper`)
- `kind`: Type of resource (e.g., `skill`, `agent`, `workflow`)
- `status`: Lifecycle state (e.g., `draft`, `active`, `deprecated`)
- `interfaces`: 
    - `cli`: Command mapping and status (enabled/disabled)
    - `webapp`: Web configuration (port, entrypoint, enabled)
- `tags`: List of descriptive hashtags (e.g., `[#automation, #browser, #social-media]`)
- `usage_guidelines`:
    - `preferred_scenarios`: List of situations where this resource excels.
    - `constraints`: Technical or operational limitations (e.g., "Requires GUI", "Rate-limited").
    - `antipatterns`: When NOT to use this resource.
- `dependencies`:
    - `resources`: List of internal resource IDs (e.g., `[chrome-remote-browser-control]`)
    - `system`: List of OS-level requirements (e.g., `[python >= 3.10, google-chrome]`)
    - `packages`: List of package manager requirements:
        - `manager`: (e.g., `pip`, `npm`, `cargo`)
        - `name`: Package name
        - `version`: Optional version constraint
- `dependents`: List of internal resource IDs that potentially depend on or consume this resource (e.g., `[linkedin, x-remote-control]`)

## Naming Standards

- **Folders**: `kebab-case` (e.g., `memory-packs`, `advanced-coder`)
- **Files**: `kebab-case` or `snake_case` depending on the language, but consistency is key.
- **IDs**: Must match the folder name in `resources/`.

## Platform Overlays

If a resource needs specific behavior for a platform like Hermes, place it in `platforms/hermes/`.
Example:
- `resources/skills/web-search/platforms/hermes/SKILL.md`
- `resources/memory-packs/coding-standards/platforms/hermes/`

## Cross-Skill Awareness Protocol

To ensure a cohesive ecosystem, all resources must adhere to these awareness rules:

### 1. Resource Interdependency
- **General Utilities**: Before starting any network service or webapp, skills MUST use `general-utilities` to verify port availability. If a port is occupied, the skill should either find a free port or offer to manage the existing process.
- **Analytics & Observability**: Every significant action (starting a server, finishing a complex task, encountering an error) SHOULD be logged using the `analytics-dashboard` event tracker.

### 2. Standardized Logging
Agents and skills should not create arbitrary log files. Use the standard path:
`runtime/{{agent_id}}/{{env}}/{{resource_id}}/{{session_id}}/events.jsonl`

### 3. Graceful Failures
If a dependency (like a specific port or another skill) is unavailable, provide a clear, actionable message via the CLI or Web interface.
