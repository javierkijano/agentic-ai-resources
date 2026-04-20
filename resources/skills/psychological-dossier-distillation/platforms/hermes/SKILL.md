---
name: psychological-dossier-distillation
description: Recover a user's psychological/biographical dossier from legacy files, preserve sensitive raw material locally, create a short operational model, and queue a distilled Hindsight entry safely.
---

# Psychological Dossier Distillation

Use when a user says they already have documents with their biography, clinical history, trauma, family background, addiction/risk history, or psychological profile, and wants it organized into something useful and always available.

## Goals
1. Find the existing source documents.
2. Preserve long sensitive material in local files.
3. Create one long consolidated draft.
4. Create one short operational/world-model document for daily use.
5. Store only a distilled stable summary in Hindsight.
6. If Hindsight is unavailable, append to `~/.hermes/Hindsight.pending.json` instead of losing the write.

## Workflow

### 1. Inventory the sources
Look for files like:
- `PROFILE_*`
- `BIOGRAFIA_*`
- `DOSSIER_*CLINICO*`
- `TAREA_PENDIENTE_ENTREVISTA_BIOGRAFICA*`
- recovered chat/psychology compilations

Use file search first. Do not guess paths.

### 2. Read the structured files before the giant raw ones
Preferred reading order:
1. short profile
2. personal profile
3. clinical profile
4. interview task / gap list
5. chronological biography / long raw biography

This gives shape before drowning in raw material.

### 3. Build a clean recovery folder
Create something like:
- `~/.hermes/recovered/<topic>/README.md`
- long draft document
- short operational model document

The README should record sources and what was intentionally kept local.

### 4. Separate the outputs
Produce at least two artifacts:

#### A. Long draft
Purpose: preserve important narrative, chronology, themes, gaps.
Include:
- cognitive/functional profile
- family of origin
- adolescence/risk/substances
- reconstruction / studies / work
- couple / family / children
- current suffering
- strengths
- risks
- missing gaps

#### B. Short operational model
Purpose: be "always at hand".
It should explain:
- what fundamentally drives this person
- what wounds/sensitivities dominate
- typical collapse sequence
- what kind of help works
- what to avoid

Think of it as a working model, not a diagnosis.

### 5. Hindsight write policy
Do **not** dump the full sensitive dossier into Hindsight by default.
Instead, store a **distilled stable operational model** only.
Examples of good Hindsight content:
- core drivers
- recurring triggers
- stable support style
- collapse sequence
- key relationship between ability and regulation

Examples of bad Hindsight content unless explicitly requested:
- detailed drug history
- explicit trauma scenes
- long criminal episodes
- raw biographical narrative

### 6. Fallback if Hindsight is down
If `hindsight_retain` fails, append an entry to:
- `~/.hermes/Hindsight.pending.json`

Suggested schema:
```json
[
  {
    "at": "ISO_TIMESTAMP",
    "context": "short label",
    "content": "distilled hindsight content",
    "source": "manual fallback after hindsight_retain connection failure",
    "last_error": "..."
  }
]
```

Append, do not overwrite existing pending entries.

## Pitfalls
- Overwriting raw files instead of creating curated outputs.
- Treating a long mixed-source document like a clean fact table.
- Stuffing highly sensitive history into always-loaded memory.
- Writing a vague motivational summary instead of a usable operational model.
- Losing the Hindsight write when the service is down instead of queueing it.

## Deliverables checklist
- [ ] recovery README
- [ ] long consolidated draft
- [ ] short operational/world-model file
- [ ] distilled Hindsight entry attempted
- [ ] pending fallback written if Hindsight unavailable
