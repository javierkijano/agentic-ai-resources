---
title: Hermes Skills System
created: 2026-04-18
updated: 2026-04-18
type: concept
tags: [hermes, agentic-ai, architecture, AI]
sources:
  - raw/articles/hermes-memory-behavior-research-2026.md
---

# Hermes Skills System

Skills are Hermes' procedural memory: on-demand knowledge documents that package repeatable workflows, conventions, and tool use patterns.

## Core idea

A skill is not a memory note. It is a reusable procedure.

That means skills are best for things like:

- a stable workflow you keep repeating
- a tool-specific procedure
- a domain playbook with steps and pitfalls
- a reusable action that should become a slash command

## Where skills live

All skills live in `~/.hermes/skills/`, which is the source of truth for the local instance.

Hermes can also scan external skill directories alongside the local one.

On a fresh install, bundled skills are copied into the local skills directory. Skills created by the agent or installed from a hub also end up there.

## Progressive disclosure

Skills are loaded only when needed.

The documented loading ladder is:

- `skills_list()` for the index
- `skill_view(name)` for the full skill
- `skill_view(name, path)` for a linked reference file

This keeps token usage down and avoids loading every procedure up front.

## Skill format

A skill usually has a `SKILL.md` file with frontmatter and a concise body.

Typical sections include:

- When to Use
- Procedure
- Pitfalls
- Verification

Skills can also ship with linked reference files, templates, scripts, and assets.

## How skills become behavior

Skills are exposed as slash commands and natural-language loadable capabilities.

When a skill becomes the right tool, Hermes can load it and follow its procedure instead of improvising from scratch.

This is one of the main reasons Hermes gets more reliable with repeated use: repeated work gets formalized into a reusable procedure.

## Skills vs memory

- Memory stores facts, preferences, and durable notes.
- Skills store procedures.
- Context files store project instructions.
- External memory stores additional cross-session context.

If you want a rule that should be followed every time in a project, use context files.
If you want a procedure that should be reused across tasks, use a skill.
If you want to remember a stable fact or preference, use memory.

## Related concepts

- [[memory-system]]
- [[personality-and-context-files]]
- [[memory-providers]]
- [[learning-loop]]
- [[hermes-architecture]]
