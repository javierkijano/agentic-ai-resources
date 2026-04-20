---
title: OpenClaw Architecture
created: 2026-04-18
updated: 2026-04-18
type: concept
tags: [architecture, agent, framework, openclaw, messaging, memory]
sources: [raw/articles/openclaw-architecture-medium.md, raw/articles/openclaw-guide-skywork.md]
---

# OpenClaw Architecture

> A deep dive into the technical architecture, memory systems, and execution loops of the OpenClaw AI agent framework.

OpenClaw is designed as a Hub-and-Spoke architecture that acts as a control plane between raw LLM API calls and user inputs across various messaging and digital platforms.

## 1. The Gateway (Orchestration Layer)

Real agents require an orchestration layer to handle queuing and state management rather than exposing raw LLM API calls directly to users or systems.

OpenClaw runs as a **local gateway process** (Node 24+):
- **Channel Adapters**: These adapt diverse inputs from WhatsApp, Slack, Telegram, or Voice into a normalized, consistent message object. This ensures the LLM receives clean data regardless of the source.
- **Routing & Sessions**: Handles multi-agent routing. If multiple messages arrive via a channel simultaneously, the gateway serializes execution via a Command Queue. This prevents tool conflicts or state corruption (e.g., two agents trying to write to the same file at once).
- **Communication**: Clients and components connect to the gateway via WebSocket.

## 2. The Agentic Loop (ReAct Pattern)

At its core, OpenClaw executes a specific, repeating ReAct (Reason + Act) loop:
`Intake → Context Assembly → Model Inference → Tool Execution → Streaming Replies → Persistence`

*   **Context Assembly**: The system builds the prompt dynamically. It layers the *Base Prompt* (core OS instructions), a *Skills Prompt* (a compact index of available tools), the *Bootstrap Context* (like `SOUL.md` or `MEMORY.md`), and *Per-run Overrides* (the current task/message).
*   **Tool Execution**: When the LLM decides to invoke a tool, it outputs a structured tool call. The OpenClaw runtime intercepts this, pauses the model, executes the real-world tool (e.g., reading a file, searching the web), and feeds the output back into the context window for the model to continue reasoning.

## 3. Skills and MCP (Model Context Protocol)

OpenClaw uses a file-based skill system alongside standardized protocols.
*   **The SKILL.md Pattern**: Tools are packaged in folders containing a `SKILL.md` file with natural language instructions for the LLM. To save context space, OpenClaw only loads the full skill text into context if the model requests it based on a high-level summary.
*   **MCP Integration**: OpenClaw embraces the Model Context Protocol (MCP) as a standardized tool layer, allowing it to connect to external services (Notion, Google Calendar) using tools that are portable across different agent frameworks.

## 4. Memory System (Markdown/SQLite)

Unlike systems relying entirely on complex vector databases, OpenClaw leans heavily into a **file-based Markdown system** located in `~/.openclaw/workspace`.

| File | Purpose |
| :--- | :--- |
| `SOUL.md` | Defines the agent's personality, tone, and directives. |
| `MEMORY.md` | Stores long-term, curated facts (e.g., "User prefers Next.js"). |
| `HEARTBEAT.md` | A proactive task checklist used by the cron/scheduler system. |
| `memory/YYYY-MM-DD.md` | Daily ephemeral logs. OpenClaw searches these on-demand. |

*Context Compaction*: When the context window fills up, the framework summarizes older conversational turns into compressed narrative entries to preserve semantic meaning without eating token limits.

## 5. Proactivity: The Heartbeat

Unlike highly reactive chatbots, OpenClaw features proactive behavior.
It runs a **scheduled trigger** (the Heartbeat). The agent wakes up, checks `HEARTBEAT.md` for pending tasks or cron-jobs, and if action is needed, it executes the tools and messages the user. If nothing is pending, it returns a silent `HEARTBEAT_OK` state.

## 6. Security and Sandboxing Sandbox

Because OpenClaw is designed to have file-system and browser access, security is paramount.
- By default, it operates with high privileges, but the framework strongly recommends running secondary agents or untrusted skills (from "ClawHub") in **isolated Docker containers**.
- In 2026, enterprise forks like *DefenseClaw* and *NemoClaw* were introduced specifically to handle infrastructure-level sandboxing (e.g., deny-by-default network access) to prevent data exfiltration.

*See also: [[entities/openclaw]], [[concepts/memory-providers]]*
