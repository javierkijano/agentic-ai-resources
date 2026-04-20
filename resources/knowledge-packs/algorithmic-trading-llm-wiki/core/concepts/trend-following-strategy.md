---
title: Trend Following Strategy
created: 2026-04-18
updated: 2026-04-18
type: concept
tags: [momentum]
sources: [raw/articles/investopedia-basics-algo-trading.md]
---
# Trend Following Strategy

## Definition
Trend following is one of the most common and straightforward algorithmic trading strategies. It involves algorithms that automatically execute buy or sell orders when price trends are identified, without attempting to forecast future prices. 

## Current State of Knowledge
The strategy relies on established technical indicators to trigger trades when specific mathematical conditions are met, such as:
- **Moving Averages:** Buying when a short-term moving average (e.g., 50-day) crosses above a long-term moving average (e.g., 200-day), and selling when it falls below.
- **Channel Breakouts:** Trading when a price breaks out of its historical trading range or "channel."
- **Price Level Movements:** Executing trades based on predefined support and resistance levels.

Because trend following does not require complex predictive modeling or price forecasting, it is generally simpler to implement than strategies like [[mean-reversion-strategy]] or those requiring advanced [[machine-learning-in-trading]].

## Related Concepts
- [[algorithmic-trading]]
- [[mean-reversion-strategy]]