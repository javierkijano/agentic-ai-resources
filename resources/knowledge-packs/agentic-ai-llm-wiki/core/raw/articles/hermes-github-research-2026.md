# Hermes Agent - GitHub Research (2026)

**Source:** Web search across `github.com/NousResearch/hermes-agent` and related repositories.
**Date:** 2026-04-18

## Overview
Hermes Agent is an autonomous AI agent built by Nous Research. It is marketed as "The agent that grows with you" due to its built-in learning loop that allows it to dynamically create and optimize skills.

## Architecture and Core Features
- **Self-Evolution:** Utilizes a dedicated module (`NousResearch/hermes-agent-self-evolution`) leveraging DSPy and GEPA (Generic Evolutionary Prompts) to optimize its own skills, prompts, and code.
- **Model Support:** Integrated with the Nous Portal to access over 400 inference models.
- **Skill Marketplace:** Ecosystem supported by tools like `hermes-link` (by joyboy257) for one-command discovery and installation of capabilities.

## Open Issues and Active Development
- **Context Compression Bug (#8923):** The default configuration for context compression silently fails for users whose auto-detection chain doesn't include OpenRouter.
- **UX/Safety Flow (#10639):** The agent currently cannot pre-anticipate dangerous command approvals, interrupting the user flow when high-risk commands are generated.
- **OS Compatibility:** Open issue (#9196) tracking the roadmap for Native Windows support. macOS IPv6 socket path limits causing bugs with SSH ControlMaster (#11842).

## Complementary Ecosystem Projects
- **Hermes WebUI:** (`nesquena/hermes-webui`) Provides a remote web/mobile interface for the CLI agent.
- **Hermes Agent Desktop:** (`Felix-Forever/hermes-agent-desktop`) A graphical client designed to orchestrate Multi-Agent workflows ("Turn Hermes into a full AI team").
- **Ship Safe:** (`asamassekou10/ship-safe`) Specialized agents purpose-built for Hermes deployments.
