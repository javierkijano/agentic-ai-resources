# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, archive, delete
> When this file exceeds 500 entries, rotate: rename to log-YYYY.md, start fresh.

## [2026-04-18] ingest | Investigated sources for algorithmic trading strategies
- Ingested core concepts from Investopedia ("Basics of Algorithmic Trading") and an academic paper repository (Manjunath.R / GitHub).
- Created `concepts/algorithmic-trading.md` covering advantages, execution types, and technical requirements.
- Created `concepts/machine-learning-in-trading.md` detailing Deep Learning and RL approaches to trading.
- Created `concepts/mean-reversion-strategy.md` 
- Created `concepts/trend-following-strategy.md`

## [2026-04-18] ingest | Added advanced LLM & RL frameworks
- Ingested papers from arXiv (FinGPT: 2306.06031, TradingAgents: 2412.20138, RL-Sentiment: 2510.10526) and a Medium article on LLM-Guided RL.
- Created `entities/fingpt.md`: documentation of the open-source financial LLM.
- Created `concepts/multi-agent-trading-frameworks.md`: detailing specialized agent societies (Analysts, Risk Managers).
- Created `concepts/llm-guided-reinforcement-learning.md`: covering the hybrid signal fusion (TD3 algorithm) and strategist/executioner models.
- Updated `index.md` with new entries and page count.