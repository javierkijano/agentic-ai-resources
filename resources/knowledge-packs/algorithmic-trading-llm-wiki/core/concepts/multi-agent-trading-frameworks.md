---
title: Multi-Agent Trading Frameworks
created: 2026-04-18
updated: 2026-04-18
type: concept
tags: [agents, llm, risk-management]
sources: [raw/articles/trading-agents-arxiv.md, raw/articles/llm-guided-rl-medium.md]
---
# Multi-Agent Trading Frameworks

## Definition
Multi-agent trading frameworks utilize a "society" of specialized Large Language Model (LLM) agents to simulate the collaborative and competitive dynamics of a professional trading firm. This approach addresses the limitations of single-agent LLM systems, such as confirmation bias and logical hallucinations.

## Key Architectures based on Recent Research

### The "TradingAgents" Architecture (Xiao et al., 2024)
A framework designed to replicate institutional roles:
- **Analyst Agents:** Specialized in Fundamental, Sentiment, and Technical analysis to process distinct data streams.
- **Researchers:** Divided into adversarial "Bull" and "Bear" agents tasked with debating the market to mitigate confirmation bias.
- **Risk Management Team:** A dedicated agent ensuring the portfolio remains within defined parameters (e.g., stop-loss, take-profit).
- **The Trader Agent:** Synthesizes the debate outcomes and insights from all other agents to execute the final trades.

### The "LLM-Guided RL" Architecture
A hybrid approach combining LLMs with [[reinforcement-learning]]:
- **Strategist Agent (LLM):** Generates high-level strategies over fixed horizons by assessing fundamentals and macroeconomic news.
- **Analyst Agent (LLM):** Converts unstructured news into quantified directional factors.
- **RL Execution Agent:** Performs the real-time, high-frequency trades based on price action while remaining constrained by the Strategist's guardrails.

## Advantages over Single-Agent Systems
- **Adversarial Debate:** Forces the system to explicitly consider counter-arguments, reducing downside risk (Max Drawdown).
- **Interpretability:** Institutional-style division of labor makes it easier for human operators to understand *why* a trade was executed.

## Related Concepts
- [[llm-in-trading]]
- [[reinforcement-learning]]