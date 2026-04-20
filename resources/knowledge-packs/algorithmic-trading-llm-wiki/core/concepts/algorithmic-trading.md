---
title: Algorithmic Trading
created: 2026-04-18
updated: 2026-04-18
type: concept
tags: [algorithmic-trading, execution, backtesting]
sources: [raw/articles/investopedia-basics-algo-trading.md, raw/articles/github-algorithmic-trading-papers.md]
---
# Algorithmic Trading

## Definition
Also known as automated or black-box trading, algorithmic trading utilizes computer programs to execute trades based on a defined set of instructions (mathematical models or rules). These systems operate at high speeds and frequencies, eliminating emotional bias and manual entry mistakes.

## Core Advantages & Disadvantages
| Pros | Cons |
| :--- | :--- |
| **Best Execution:** Fast order placement. | **Latency Risk:** Delays can negate profits. |
| **Low Latency:** Avoids slippage. | **Black Swan Events:** Models may fail during unprecedented disruptions. |
| **Backtesting:** Strategies validated against historical data. | **Technical Dependence:** Vulnerable to system failures and connectivity issues. |
| **No Human Error:** Eliminates emotional bias. | **High Costs:** Significant capital needed for development and data. |
| **Reduced Costs:** Lower transaction costs. | **Market Impact:** Large trades can cause "flash crashes." |

## Common Strategies
1. **[[trend-following-strategy]]:** Using technical indicators like moving averages.
2. **[[mean-reversion-strategy]]:** Betting prices will return to historical averages.
3. **Arbitrage:** Exploiting price discrepancies between markets.
4. **Index Fund Rebalancing:** Capitalizing on index adjustments.
5. **Execution-Focused:** VWAP (Volume-Weighted Average Price), TWAP (Time-Weighted Average Price), POV (Percentage of Volume).
6. **Mathematical Models:** Delta-neutral strategies and other complex quantitative approaches (increasingly driven by [[machine-learning-in-trading]]).

## Technical Requirements
- **Programming:** C++ for high-frequency trading (HFT) latency, Python for data analysis and development.
- **Market Data:** Access to real-time price feeds.
- **Infrastructure:** Network connectivity to exchanges and order routing platforms (often leveraging GPUs for ML tasks).
- **Backtesting:** Crucial for validating strategy viability.

## Regulatory Landscape
While algorithmic trading is legal, its impact on market liquidity and potential to cause disruptions (like the 2010 Flash Crash) remains a topic of regulatory scrutiny. Currently, high-frequency algorithms operate in the microsecond or nanosecond timescale.