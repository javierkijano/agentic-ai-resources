---
title: Hindsight Memory System
created: 2026-04-18
updated: 2026-04-18
type: concept
tags: [memory, architecture, system]
sources: [raw/articles/hindsight-docs.md]
---

# Hindsight Documentation

Source: https://hindsight.vectorize.io/

## Overview
Hindsight is a specialized memory system for AI agents, replacing traditional vector search with a system offering long-term context, temporal reasoning, and knowledge consolidation.

## Core Actions
1. **`retain()`**: Store information.
2. **`recall()`**: Multi-strategy search.
3. **`reflect()`**: Reason over memories.

## Memory Hierarchy (Priority for Reflection)
1. **Mental Models**: Curated summaries.
2. **Observations**: Automatically consolidated facts.
3. **World Facts**: Objective external data.
4. **Experience Facts**: AI action records.

## Key Components
*   **TEMPR Retrieval**: Parallel use of Semantic, Keyword (BM25), Graph, and Temporal searching.
*   **Observation Consolidation**: Deduplication, evidence tracking, continuous refinement, and freshness scoring.
*   **Agent Config**: Mission (identity), Directives (rules), and Disposition (traits like empathy or literalism) configuration.

## Ecosystem
*   **Languages**: Python, TS/Node.js, Go, CLI, HTTP API.
*   **Deployment**: Docker Compose, Helm, Pip.
