---
title: Hermes Architecture
created: 2026-04-14
updated: 2026-04-14
type: concept
tags: [hermes, architecture, agentic-ai]
sources:
  - raw/articles/hermes-architecture-spec.md
---

# Hermes Architecture

The architecture of Hermes is designed for flexibility and autonomous operation. Key components include:

-   **Core Agent Loop:** Manages perception, decision-making, and action execution.
-   **Skills System:** Handles procedural memory, allowing agents to create, improve, and reuse skills.
-   **Memory System:** Provides persistent storage for learned information, user models, and session context.
-   **Tool Integration:** Interfaces with a wide array of tools, managed through a configurable toolset system.
-   **Messaging Gateway:** Enables interaction via platforms like Telegram and Discord.
-   **Configuration System:** Allows detailed setup of models, providers, and agent behavior.

[[hermes]] is the primary entity utilizing this architecture.
