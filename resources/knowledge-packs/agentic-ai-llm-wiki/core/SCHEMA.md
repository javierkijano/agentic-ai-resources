# Wiki Schema

## Domain
Technology > Agentic AI. Focused on agentic AI systems, including Hermes and related platforms.

## Conventions
- File names: lowercase, hyphens, no spaces (e.g., `hermes.md`, `agentic-ai.md`)
- Every wiki page starts with YAML frontmatter (see example)
- Use [[wikilinks]] to link between pages (minimum 2 outbound links per page)
- On update, bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- All actions appended to `log.md`

## Frontmatter
Example:
---
title: Some Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [technology, agentic-ai]
sources: []
---

## Tag Taxonomy
- technology
- agentic-ai
- hermes
- agent
- autonomy
- architecture
- model
- algorithm
- safety
- alignment
- governance
- RL
- optimization
- AI
- ethics
- deployment
- scalability
- data
- evaluation
- open-source
- memory
- system
- models
- reasoning
- coding
- comparison
- framework
- openclaw
- messaging
- documentation
- overview
- autonomous-agent
- learning-loop
- knowledge-base
- wiki

(Note: We'll expand this as needed; all page tags must be from this taxonomy.)

## Page Thresholds
- Create a page when an entity/concept appears in 2+ sources OR is central to one source
- Add to existing page when new source mentions
- Do not create pages for passing mentions
- Every page must link to at least 2 other pages

## Entity Pages
One page per notable entity. Include overview, key facts, relationships, sources.

## Concept Pages
Definition, current state, open questions, related concepts.

## Comparison Pages
Side-by-side analyses.

## Update Policy
When new information conflicts:
1. Check dates
2. If contradictory, note both with dates/sources
3. Mark contradictions: `contradictions: [page-name]` in frontmatter
4. Flag for user review in lint

## index.md Template
# Wiki Index

> Content catalog. Every wiki page listed under its type with a one-line summary.
> Read this first to find relevant pages for any query.
> Last updated: 2026-04-14 | Total pages: 0

## Entities

## Concepts

## Comparisons

## Queries

(Note: If any section grows beyond 50 entries, split; if total pages >200, add _meta/topic-map.md.)

## log.md Template
# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, archive, delete
> When this file exceeds 500 entries, rotate: rename to log-YYYY.md, start fresh.

## [YYYY-MM-DD] create | Wiki initialized
- Domain: Technology
- Structure created with SCHEMA.md, index.md, log.md

