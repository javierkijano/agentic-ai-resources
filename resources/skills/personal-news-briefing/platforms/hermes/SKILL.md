---
name: personal-news-briefing
description: "Canonical news-intelligence skill for Javier. Uses X trend pages as signal, specialized sources as validation, and also guides the news-intelligence app/MVP. Replaces news-intel-mvp."
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [news, briefing, monitoring, x, trends, youtube, app, product, personalization]
---

# Personal News Intelligence

Single canonical skill for:
- daily news briefing / monitoring
- spotting candidate topics in X trend pages
- validating topics in specialized sources
- building or extending the news-intelligence app / MVP

It replaces:
- `news-intel-mvp`

## When to use
Use when Javier asks for:
- a daily political/geopolitical/economic briefing
- source curation or monitoring
- checking whether a trend deserves deeper coverage
- a news-intelligence web app, dashboard, or MVP
- workflow or product changes to the briefing system

## Core principle
Do NOT produce exhaustive feed dumps.
This is a profile-first system, not a channel-first system.

Instead, learn the user's interests over time and send a selective briefing:
- priority alta = vigilancia principal
- priority media/baja = señales, contexto y recomendaciones
- topic weights matter more than any fixed source list
- use X and web together to infer what matters and what fits Javier
- if sources disagree, say so explicitly

## Javier's editorial preferences
- Main interest: geopolítica y política nacional
- Also relevant: economía y mercados
- Strong structural interests: vivienda/regulación inmobiliaria, inmigración en Europa, corrupción del entorno de Pedro Sánchez, política argentina/Milei, Cuba/Venezuela, crisis humanitarias/genocidios
- IA is usually secondary unless it is clearly game changing or a major policy/market shift
- High priority means "watch first", not "summarize everything"
- Medium/low priority sources can still be valuable for context or recommendations
- Include under-covered but morally significant crises when relevant, not just dominant trending topics

## Source model

### Tier 1 — What is happening now
Use fast-moving sources to detect the day's important stories:
- X / Twitter signals
- public X trend pages / trend aggregators as lead generators
- breaking-news or current-affairs sources
- high-priority YouTube channels that react quickly to the news

### X trend pages as lead generator
When a topic is bubbling on X, use trend pages first to discover the topic, then validate it elsewhere.
Good sources include public trend pages and explore pages such as:
- trends24
- getdaytrends
- xtrends
- globaltwittertrends
- X Explore when accessible

Rule:
- treat trend pages as a noisy signal, not as authoritative coverage
- if a trend looks newsworthy, turn it into search queries for specialized sources
- cross-check with local press, Reuters/AP, official statements, niche experts, and topic-specific YouTube channels before including it in the briefing

### Tier 2 — Who explains it best
Use YouTube and commentary sources to add:
- context
- competing interpretations
- why it matters
- what to watch next

### Tier 3 — Recommendations
Use medium/low-priority channels to surface:
- worth-reading/watching pieces
- explainers
- longer interviews
- non-urgent but high-fit items for Javier

## Briefing mode

### Output format
Target length: medium, around 5-8 points.

Structure:
1. Lo más importante hoy
   - 3-5 items
   - what happened
   - why it matters
   - early read / synthesis
   - include source links/references for each item
2. Señales que te pueden interesar
   - videos/posts/pieces matched to Javier's interests
   - include links whenever possible
3. Qué merece profundizar
   - 1-3 promising topics to expand on request
4. IA radar
   - only include if genuinely important

### Reference rule
Each briefing item should include at least one concrete source reference when available:
- X post/thread link if citing X
- YouTube video link if citing a video
- article link if citing press/web coverage
- if multiple sources shaped the synthesis, include 2-3 links max, not a giant dump

### Style rules
- concise, useful, and editorialized
- avoid filler
- do not include items just because a channel published them
- prefer synthesis over list-dumping
- if sources disagree, say so explicitly

### Learning loop
After each briefing, treat Javier's follow-up requests as training signals:
- topics he asks to expand = stronger interest
- sources he ignores repeatedly = lower effective weight
- topics he corrects or dismisses = reduce priority
- recurring asks = convert into stable editorial preference

## App / product mode

If Javier asks to build or evolve the news-intelligence app:
- use Next.js App Router + TypeScript + Tailwind
- keep it mock-data-first until the product shape stabilizes
- store feedback/follows/settings early, even if the scoring engine is simple
- keep route contracts stable so the UI can later swap in real ingestion/db queries

### Product pattern
Do NOT build a generic feed reader.
Build a panel with these core surfaces:
1. Home / daily briefing
2. Radar / raw filtered signals
3. Themes / topic pages
4. Item detail
5. Follows / dossiers
6. Archive
7. Settings

### Feedback model
Support these actions from day 1:
- MORE
- LESS
- FOLLOW
- DEEPEN
- SAVE
- DISMISS
- SOURCE_GOOD
- SOURCE_BAD
- NOISE

### Minimal API surface
Create these first if the app needs them:
- GET /api/briefings/today
- GET /api/radar
- GET /api/themes
- GET /api/themes/[slug]
- GET /api/items/[id]
- POST /api/items/[id]/feedback
- GET/POST /api/follows
- DELETE /api/follows/[id]
- GET /api/archive
- GET/POST /api/settings

### References rule for the app
Every briefing item should include 1-3 references:
- article links
- YouTube links
- X/tweet/thread links
- document/source links

Do not ship entries without traceable source references.

### Migration strategy
When ready to move from MVP to a real system:
- keep route contracts stable
- replace mock-data reads with DB queries progressively
- keep store semantics for feedback/follows/settings, then swap implementation behind them
- keep Prisma simple until the app actually needs it; if you use the classic schema workflow, keep the datasource/config migration deliberate

## Operational workflow
1. Scan fast sources for the day's main stories
   - start with RSS/web sources for broad coverage
   - also check public X trend pages / trend aggregators first to surface candidate topics that may not yet be covered in specialist media
   - use these signals to identify the 1-3 dominant themes before touching channel-specific content
2. Cross-check with Javier's high-priority channels
   - open the channel's /videos page directly when useful
   - if YouTube shows consent, reject non-essential cookies and continue
   - do not depend on yt-dlp being installed; browser + public page access is a reliable fallback
3. Pull medium/low-priority signals only if they add context or strong fit
4. Select the best 5-8 items, not the most recent 5-8 items
   - cluster raw inputs into themes, then choose themes, not uploads
5. Deliver the briefing
6. When Javier asks to deepen a topic, produce a second-layer analysis with more context, source comparison, and implications

## Important reminders
- This is a personalized briefing, not a feed dump
- High priority channels are radar, not a mandate to summarize all uploads
- Use X + web + YouTube together to infer what matters in the world and what fits Javier specifically
- Channel lists are provisional and continuously learned, not fixed configuration
