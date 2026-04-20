---
title: Machine Learning in Trading
created: 2026-04-18
updated: 2026-04-18
type: concept
tags: [predictive-modeling, reinforcement-learning, llm]
sources: [raw/articles/github-algorithmic-trading-papers.md]
---
# Machine Learning in Trading

## Definition
The application of Machine Learning (ML), specifically Deep Learning (DL) and Reinforcement Learning (RL), to algorithmic trading. This involves using algorithms that can "learn" and adapt their strategies based on historical and real-time market data.

## Current State of Knowledge
Recent academic research is significantly focused on integrating complex neural networks and autonomous agents into trading systems:

### 1. Deep Learning & Neural Networks
- Used for predictive modeling of financial markets.
- Applied to High-Frequency Trading (HFT) and Limit Order Books to predict micro-price movements.
- Architectures include Convolutional Neural Networks (CNNs) for analyzing technical charts and Deep Residual Learning with attention mechanisms for portfolio optimization.

### 2. Reinforcement Learning (RL)
- Viewed as playing [[financial-trading-as-a-game]].
- Used for dynamic portfolio management and stock/FX trading.
- Advanced implementations use Recurrent Reinforcement Learning and LSTM networks to build autonomous trading agents.

### 3. Alternative Data Analysis
- **Sentiment Analysis:** Improving decision-making using Deep Learning applied to financial disclosures and news analytics.
- Algorithms are trained to "read" the news before human traders and execute trades based on sentiment (often using NLP models, evolving toward [[llm-in-trading]]).

## Advanced Applications
- Generative Adversarial Networks (GANs) to generate realistic simulated stock market order streams for backtesting.
- Information Theory and its relationship with algorithmic trading in understanding market ignorance/liquidity.

## Related Concepts
- [[algorithmic-trading]]
- [[reinforcement-learning]]
- [[financial-trading-as-a-game]]