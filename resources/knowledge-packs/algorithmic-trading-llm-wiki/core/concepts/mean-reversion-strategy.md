---
title: Mean Reversion Strategy
created: 2026-04-18
updated: 2026-04-18
type: concept
tags: [mean-reversion]
sources: [raw/articles/investopedia-basics-algo-trading.md, raw/articles/github-algorithmic-trading-papers.md]
---
# Mean Reversion Strategy

## Definition
Mean reversion is a core algorithmic trading strategy based on the statistical theory that asset prices, volatility, and historical returns will eventually revert to their long-term mean or average level. The underlying assumption is that extreme price movements are temporary.

## Current State of Knowledge
In algorithmic trading, mean reversion models identify overbought or oversold conditions. Algorithms monitor prices against historical averages (e.g., moving averages) and automatically execute trades:
- **Buy** when the asset price falls significantly below its historical average.
- **Sell** (or short) when the price rises significantly above its historical average.

This strategy is particularly effective in ranging markets, as opposed to trending markets.

## Advanced Implementations
According to recent research (e.g., *Profitable Algorithmic Trading Strategies in Mean-Reverting Markets*), advanced mean reversion strategies are often enhanced using:
- [[reinforcement-learning]] to dynamically adjust the parameters of what constitutes an "extreme" deviation.
- Statistical arbitrage pairs trading, where the spread between two historically correlated assets is traded when it diverges from its mean.

## Related Concepts
- [[algorithmic-trading]]
- [[trend-following-strategy]]
- [[reinforcement-learning]]