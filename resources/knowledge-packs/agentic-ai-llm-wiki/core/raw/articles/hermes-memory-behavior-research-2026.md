Hermes Memory, Personality, Context, Skills, and Learning Research

This note collates the official Hermes docs, the live local configuration, and the current memory state on this machine. It is a source dossier for the wiki pages that summarize the behavior stack.

Sources consulted:
- https://hermes-agent.nousresearch.com/docs/
- https://hermes-agent.nousresearch.com/docs/user-guide/features/memory
- https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers
- https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
- https://hermes-agent.nousresearch.com/docs/user-guide/features/personality
- https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files
- https://hermes-agent.nousresearch.com/docs/developer-guide/prompt-assembly
- https://hermes-agent.nousresearch.com/docs/developer-guide/architecture
- https://hermes-agent.nousresearch.com/docs/developer-guide/agent-loop/
- https://github.com/NousResearch/hermes-agent-self-evolution
- https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md
- ~/.hermes/config.yaml
- ~/.hermes/SOUL.md
- ~/.hermes/memories/MEMORY.md
- ~/.hermes/memories/USER.md
- hermes memory status

Key findings:
- Hermes memory is layered. It is not a single database or a single file.
- The built-in memory is split into MEMORY.md and USER.md inside ~/.hermes/memories/.
- MEMORY.md stores agent notes: environment facts, conventions, lessons learned, and tool workarounds.
- USER.md stores the user profile: preferences, communication style, and stable expectations.
- The built-in memory snapshot is frozen into the system prompt at session start.
- The memory tool supports add, replace, and remove. There is no read action because memory is already injected into context.
- External memory providers are additive. The built-in memory always stays active.
- Only one external memory provider is active at a time.
- This installation currently uses hindsight as the active provider.
- Hermes also exposes installed provider plugins such as honcho, mem0, openviking, retaindb, byterover, supermemory, and holographic.
- SOUL.md is the primary identity file. It lives in HERMES_HOME and is loaded only from there.
- Project context files include .hermes.md / HERMES.md, AGENTS.md, CLAUDE.md, .cursorrules, and .cursor/rules/*.mdc.
- Only one project context type is loaded per session: .hermes.md → AGENTS.md → CLAUDE.md → .cursorrules.
- Context files are progressively discovered as Hermes walks directories, and they are security-scanned before injection.
- Skills live in ~/.hermes/skills/ and use progressive disclosure so the agent only loads what it needs.
- Hermes has a built-in learning loop: it creates skills from experience, improves them during use, nudges itself to persist knowledge, and builds a deeper user model across sessions.
- Hermes Agent Self-Evolution is a separate repo that optimizes skills, prompts, tool descriptions, and code using DSPy + GEPA and related optimizers.
- That self-evolution stack operates on Hermes via API calls; it does not imply online model-weight training inside the runtime loop.
- The agent loop assembles the system prompt in a stable order to preserve prompt cache behavior.
- Session history is stored in SQLite with FTS5 and can be searched with session_search.
- Behavior is shaped by identity, project instructions, bounded memory, external providers, skills, and config knobs.

Prompt assembly order (high level):
1. Agent identity from SOUL.md
2. Tool-aware behavior guidance
3. Optional Honcho static block
4. Optional system message override
5. Frozen MEMORY.md snapshot
6. Frozen USER.md snapshot
7. Skills index
8. Context files (AGENTS.md, .cursorrules, .cursor/rules/*.mdc)
9. Timestamp / optional session metadata
10. Platform hint

Local config notes:
- memory.provider = hindsight
- memory_char_limit = 2200
- user_char_limit = 1375
- nudge_interval = 10
- flush_min_turns = 6

Practical takeaway:
Hermes learns mostly by updating what it remembers, what skills it has, and what context it loads. The behavior stack is explicit and inspectable, not hidden in a single prompt blob.
