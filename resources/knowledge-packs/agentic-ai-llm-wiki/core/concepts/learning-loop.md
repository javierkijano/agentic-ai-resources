---
title: Hermes Learning Loop and Self-Evolution
created: 2026-04-18
updated: 2026-04-20
type: concept
tags: [hermes, agentic-ai, AI, optimization]
sources:
  - raw/articles/hermes-memory-behavior-research-2026.md
  - raw/articles/hermes-behavior-stack-dossier-2026-04-20.md
---

# Hermes Learning Loop and Self-Evolution

Hermes' documented learning loop is operational and artifact-based. The core idea is not "the model rewrites itself every turn", but that useful experience gets promoted into durable behavior surfaces.

## What the docs explicitly claim

The local docs describe a built-in learning loop that can:

- create skills from experience
- improve skills during use
- nudge itself to persist useful knowledge
- build a deeper model of the user across sessions

## Runtime surfaces that actually change

In day-to-day use, Hermes mainly improves by changing inspectable artifacts:

- built-in memory entries
- user-profile entries
- skill files and their supporting references
- external memory provider state
- searchable session history that can be recalled later

That is behavior-surface evolution, not online model-weight training.

## Separate self-evolution stack

The local research materials also point to a separate `hermes-agent-self-evolution` repository.

That stack is described as operating on Hermes through things like:

- skills
- prompts
- tool descriptions
- code

The earlier local research note ties it to DSPy + GEPA, Darwinian Evolver, and DSPy MIPROv2.

## Why the separation matters

Keeping runtime learning separate from offline optimization has two benefits:

- the day-to-day behavior stack stays inspectable and reversible
- heavier optimization work can be versioned, reviewed, and run outside the live chat loop

## Related concepts

- [[memory-system]]
- [[skills-system]]
- [[built-in-memory-files]]
- [[memory-providers]]
- [[session-history-and-recall]]
