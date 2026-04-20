---
title: OpenClaw
created: 2026-04-18
updated: 2026-04-18
type: entity
tags: [agent, framework, openclaw, open-source]
sources: [raw/articles/openclaw-repo.md, raw/articles/openclaw-awesome-skills.md]
---

# OpenClaw 🦞

> A highly popular, local-first personal AI assistant framework designed to run on the user's own devices.

OpenClaw acts as a centralized control plane (Gateway) connecting messaging channels, agentic tools (skills), and AI model providers into a single, always-on assistant ecosystem.

## Key Features & Architecture

- **Local-First Gateway**: The logic and control plane reside on the user's host machine (Node 24+ recommended, supports macOS, Linux, Windows/WSL2).
- **Multi-Channel Inbox**: Deep integration with WhatsApp, Telegram, Slack, Discord, Signal, iMessage (via BlueBubbles), Teams, WeChat, Matrix, etc.
- **Agentic Routing**: Supports multi-agent systems, routing specific channels or tasks to isolated agent workspaces.
- **Voice & UI**: Offers "Voice Wake" alongside an active visual workspace using **A2UI** (Live Canvas) for interactive rendering.
- **Security & Sandboxing**: Inbound messages are treated as untrusted. Features direct-message pairing (approval codes) and optional Docker/Podman sandboxing for non-main sessions.

## Ecosystem & Skills System

OpenClaw boasts a massive ecosystem driven by its community and Registry (**ClawHub**).

- **Skill Management**: Installed via CLI (`clawhub install <skill>`), manual dropping in `~/.openclaw/skills/`, or pasting a repo URL in chat.
- **Volume & Curation**: As of early 2026, the registry holds over 13,000 skills, though curated lists filter this down to ~5,200 high-quality skills spanning coding, automation, smart home, and Apple ecosystem integrations.
- **Model Support**: Agnostic to over 25+ LLM providers, natively supporting frontier models like GPT-5.4, Claude Opus, and local models.

## Corporate & Community Backing
The project is massively popular (~360k GitHub stars) and is sponsored/backed by key AI hardware and software players including NVIDIA, OpenAI, GitHub, and Vercel. 

*See also: [[comparisons/frontier-llm-models-2026]], [[concepts/skills-system]]*
