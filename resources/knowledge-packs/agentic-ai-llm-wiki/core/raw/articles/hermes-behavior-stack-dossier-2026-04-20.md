# Hermes Behavior Stack Dossier (2026-04-20)

This dossier collects direct facts about Hermes' behavior stack from the local docs, local source code, live configuration, and live runtime checks on this machine.

It is meant to support focused wiki pages about:
- built-in memory and user profile files
- prompt assembly and behavior layering
- project context loading
- skills as procedural memory
- session history and transcript recall
- external memory providers
- runtime learning vs. offline self-evolution

## Sources consulted

Documentation inside the local Hermes checkout:
- `~/.hermes/hermes-agent/website/docs/developer-guide/prompt-assembly.md`
- `~/.hermes/hermes-agent/website/docs/developer-guide/session-storage.md`
- `~/.hermes/hermes-agent/website/docs/user-guide/features/memory.md`
- `~/.hermes/hermes-agent/website/docs/user-guide/features/memory-providers.md`
- `~/.hermes/hermes-agent/website/docs/user-guide/features/skills.md`
- `~/.hermes/hermes-agent/website/docs/user-guide/features/personality.md`
- `~/.hermes/hermes-agent/website/docs/user-guide/features/context-files.md`
- `~/.hermes/hermes-agent/website/docs/user-guide/sessions.md`
- `~/.hermes/hermes-agent/website/docs/index.md`

Local source files:
- `~/.hermes/hermes-agent/agent/prompt_builder.py`
- `~/.hermes/hermes-agent/agent/subdirectory_hints.py`
- `~/.hermes/hermes-agent/tools/memory_tool.py`
- `~/.hermes/hermes-agent/hermes_state.py`
- `~/.hermes/hermes-agent/agent/memory_manager.py`
- `~/.hermes/hermes-agent/run_agent.py`

Live local instance files and commands:
- `~/.hermes/config.yaml`
- `~/.hermes/SOUL.md`
- `~/.hermes/memories/MEMORY.md`
- `~/.hermes/memories/USER.md`
- `hermes memory status`
- direct character-count check for `MEMORY.md` and `USER.md`

Earlier local research note:
- `raw/articles/hermes-memory-behavior-research-2026.md`

## Direct facts by layer

### Identity and persona

- `SOUL.md` is the primary identity slot in the system prompt.
- Hermes loads `SOUL.md` only from `HERMES_HOME`, not from the current working directory.
- `prompt_builder.py` falls back to `DEFAULT_AGENT_IDENTITY` when `SOUL.md` is absent, empty, unreadable, or skipped.
- `SOUL.md` is security-scanned and truncated before prompt injection.
- When `SOUL.md` is used for identity, it is not duplicated again inside the project-context section.

### Built-in memory and user profile

- Hermes keeps built-in memory in two files under `~/.hermes/memories/`:
  - `MEMORY.md`
  - `USER.md`
- The configured character limits in the live instance are:
  - `memory_char_limit: 2200`
  - `user_char_limit: 1375`
- `MemoryStore.load_from_disk()` captures a frozen system-prompt snapshot at session start.
- Mid-session writes update disk immediately but do not mutate the already-built prompt snapshot.
- Entries are stored as text blocks separated by `§` and may be multiline.
- Memory content is scanned for prompt-injection and exfiltration patterns before it is accepted.
- The public memory tool schema exposes `add`, `replace`, and `remove` actions.
- Hermes documentation explicitly says there is no `read` action because the snapshot is already present in context.

### Project context and repo-local behavior

- Startup project context uses a first-match priority order:
  1. `.hermes.md` / `HERMES.md`
  2. `AGENTS.md`
  3. `CLAUDE.md`
  4. `.cursorrules` / `.cursor/rules/*.mdc`
- `.hermes.md` is searched from the current directory up to the git root.
- Startup `AGENTS.md`, `CLAUDE.md`, and `.cursorrules` are loaded from the working directory context.
- `.hermes.md` YAML frontmatter is stripped before injection.
- Context files are scanned for prompt-injection patterns and truncated before injection.
- Progressive subdirectory discovery is handled separately by `SubdirectoryHintTracker`.
- Subdirectory hints are appended to tool results instead of mutating the cached system prompt.
- Subdirectory discovery checks up to five ancestor directories and caps each discovered hint at 8,000 characters.

### Prompt assembly and behavior stack

- Hermes separates cached system-prompt state from API-call-time additions.
- The documented high-level cached prompt order is:
  1. `SOUL.md` identity
  2. tool-aware behavior guidance
  3. optional Honcho static block
  4. optional system-message override
  5. frozen `MEMORY.md` snapshot
  6. frozen `USER.md` snapshot
  7. skills index
  8. startup context files
  9. timestamp / optional session metadata
  10. platform hint
- API-call-time additions include ephemeral system prompt overlays, prefill messages, gateway overlays, and later-turn provider recall.
- The docs explicitly frame this split as a prompt-caching and correctness decision.

### Skills and procedures

- Skills are on-demand knowledge documents loaded with progressive disclosure.
- The documented loading ladder is:
  - `skills_list()`
  - `skill_view(name)`
  - `skill_view(name, path)`
- The primary local skills directory is `~/.hermes/skills/`.
- External skill directories can be scanned read-only alongside the local directory.
- Hermes docs frame skills as procedural memory, distinct from factual memory.
- The prompt guidance explicitly tells the agent to save non-trivial workflows as skills.

### Session history and recall

- Hermes stores session history in `~/.hermes/state.db`.
- `hermes_state.py` documents SQLite + WAL mode + FTS5 full-text search.
- The main persistent tables are:
  - `sessions`
  - `messages`
  - `messages_fts`
  - `schema_version`
- The database stores full message history, metadata, titles, token counts, and reasoning fields.
- `session_search` uses FTS5 ranking, groups matches by session, loads the most relevant sessions, and summarizes them with a fast model.
- Gateway transcript files also live under `~/.hermes/sessions/`.
- Docs distinguish session search from built-in memory: memory is small and always in prompt; session search is larger and used on demand.

### External memory provider

- Hermes keeps built-in memory active even when an external provider is enabled.
- Only one external memory provider can be active at a time.
- The live config sets `memory.provider: hindsight`.
- The live `hermes memory status` command reports:
  - Built-in: always active
  - Provider: hindsight
  - Plugin: installed and available
- The same status command reports additional installed plugins: byterover, holographic, honcho, mem0, openviking, retaindb, supermemory.
- Hermes docs say an active provider may:
  - inject provider context
  - prefetch memories before turns
  - sync turns after responses
  - extract memories on session end
  - mirror built-in memory writes
  - add provider-specific tools
- `memory_manager.py` wraps recalled provider context in a fenced `<memory-context>` block with a system note saying it is background, not new user input.

### Learning loop and self-improvement

- The Hermes docs home page describes a built-in learning loop.
- The documented runtime loop is behavioral and artifact-based:
  - create skills from experience
  - improve skills during use
  - nudge the agent to persist useful knowledge
  - deepen the user model across sessions
- The docs also point to a separate `hermes-agent-self-evolution` repository.
- The current wiki research note attributes that offline optimization stack to DSPy + GEPA, Darwinian Evolver, and DSPy MIPROv2.
- The runtime memory stack and the offline self-evolution stack are related but not the same mechanism.

## Local instance notes captured on 2026-04-20

- `MEMORY.md` current size: 1,469 chars.
- `USER.md` current size: 1,291 chars.
- The live config points `skills.config.wiki.path` to this wiki directory:
  - `/home/jq-hermes-01/hermes-workspace/agentic-ai/knowledge/generated/agentic-ai-llm-wiki`
- The live repo branch for `agentic-ai` is `hermes/dev`.

## Editorial boundary

This dossier keeps direct facts and live-instance checks together in one place. Concept pages derived from it should stay tighter, more stable, and more selective than this source note.
