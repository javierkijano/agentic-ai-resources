---
title: Hermes Agent
created: 2026-04-14
updated: 2026-04-18
type: entity
tags: [hermes, agentic-ai, technology]
sources: [raw/articles/hermes-github-research-2026.md]
---

# Hermes Agent

Hermes Agent is an autonomous AI agent built by [[nous-research]]. It is designed to be "the agent that grows with you" through a built-in learning loop that dynamically creates and optimizes its own skills.

## Architecture and Core Capabilities

- **Self-Evolution**: The agent leverages DSPy and GEPA (Generic Evolutionary Prompts) to optimize its skills, prompts, and code. This is tracked in a separate repository (`NousResearch/hermes-agent-self-evolution`).
- **Model Ecosystem**: Integrated tightly with the Nous Portal to access over 400 inference models.
- **Skill Management**: Has dedicated marketplace infrastructure (`hermes-link`) for discovery, installation, and management of capabilities.

## Active Development and Open Issues

As of April 2026, the primary open issues and roadmap items on GitHub include:

- **Context Compression Bug (#8923)**: The default configuration for context compression silently fails if the auto-detection chain does not include OpenRouter.
- **UX/Safety Flow (#10639)**: The agent struggles to pre-anticipate dangerous command approvals, causing interruptions in complex task execution.
- **Platform Support**: Native Windows support is still an open roadmap discussion (#9196), while macOS continues to see networking bugs like IPv6 SSH Socket path limits (#11842).

## Ecosystem Projects

The broader community around Hermes has built several complementary tools:
- **[[hermes-webui]]**: A browser and mobile-friendly interface for the CLI.
- **[[hermes-desktop]]**: A full multi-agent desktop client that orchestrates parallel teams of Hermes instances.
- **Ship Safe**: Custom deployment agents based on Hermes internals.
