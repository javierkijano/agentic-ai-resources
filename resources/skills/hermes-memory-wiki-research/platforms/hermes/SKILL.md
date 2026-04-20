---
name: hermes-memory-wiki-research
description: Investigar en serio el stack de comportamiento de Hermes y convertirlo en páginas de wiki consistentes, usando docs, código local, config viva y verificación estructural.
version: 1.0.0
author: Javier + Hermes
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [hermes, wiki, research, memory, context, skills, prompt-assembly, lint]
---

# Hermes memory wiki research

Skill específica para documentar cómo funciona Hermes de verdad en este entorno y dejar el resultado bien integrado en la wiki.

## Cuándo usar

Usar cuando Javier pida:
- investigar memoria, contexto, skills, session search, providers o learning loop de Hermes
- entender el stack de comportamiento de Hermes más allá de una lectura superficial de docs
- escribir o actualizar páginas de wiki sobre cómo Hermes piensa, recuerda o carga contexto
- convertir findings dispersos en un dossier + páginas conceptuales + actualización de índice/log

## Contexto y guardrails

Si trabajas dentro de `agentic-ai`:
1. ancla el trabajo en `/home/jq-hermes-01/hermes-workspace/agentic-ai`
2. lee `README.md` y `.hermes.md`
3. escribe solo en zonas permitidas del repo
4. para la wiki generada, trabaja en `knowledge/generated/<wiki>/`

## Resolver primero la ubicación de la wiki

No asumas solo `WIKI_PATH`.

Orden recomendado:
1. si el usuario dio una ruta explícita, usar esa
2. si existe `WIKI_PATH`, usarla
3. si no, revisar `~/.hermes/config.yaml` en `skills.config.wiki.path`
4. si tampoco existe, caer al default de la skill de wiki o preguntar

## Fuentes obligatorias

No te quedes solo con la wiki existente. Cruza al menos estas capas:

1. wiki actual
   - `SCHEMA.md`
   - `index.md`
   - últimas entradas de `log.md`

2. documentación local de Hermes
   - docs de memory
   - docs de memory providers
   - docs de skills
   - docs de personality / SOUL
   - docs de context files
   - docs de prompt assembly
   - docs de session storage / sessions

3. código local cuando haga falta confirmar comportamiento real
   - `agent/prompt_builder.py`
   - `agent/subdirectory_hints.py`
   - `tools/memory_tool.py`
   - `agent/memory_manager.py`
   - `hermes_state.py`
   - `run_agent.py`

4. estado vivo de la instancia local cuando aporte señal real
   - `~/.hermes/config.yaml`
   - `~/.hermes/SOUL.md`
   - `~/.hermes/memories/MEMORY.md`
   - `~/.hermes/memories/USER.md`
   - comandos como `hermes memory status`
   - comprobaciones puntuales de tamaños, limits o provider activo

## Capas conceptuales mínimas a cubrir

Separar explícitamente:
- identidad / persona (`SOUL.md`)
- memoria integrada (`MEMORY.md`, `USER.md`)
- contexto de proyecto (`.hermes.md`, `AGENTS.md`, etc.)
- skills / memoria procedimental
- historial de sesiones / `session_search`
- memory provider externo
- learning loop / self-evolution
- prompt assembly y diferencia entre capas cacheadas vs overlays runtime

## Forma de trabajo recomendada

1. Orientación
   - leer `SCHEMA.md`, `index.md`, `log.md`
   - buscar si ya existen páginas que cubran parte del tema

2. Dossier raw
   - crear una nota fuente en `raw/articles/`
   - separar hechos directos de inferencias
   - citar rutas, docs y comandos usados

3. Síntesis en páginas pequeñas
   - una página por subtema cuando el contenido lo merezca
   - preferir páginas focalizadas a una sola página gigante
   - usar wikilinks solo a páginas existentes o que vayas a crear en esta misma pasada

4. Actualización de navegación
   - actualizar `index.md`
   - actualizar `log.md`
   - si hace falta, ampliar taxonomía en `SCHEMA.md` antes de usar tags nuevos

5. Verificación estructural obligatoria
   - comprobar enlaces rotos
   - comprobar tags fuera de la taxonomía
   - comprobar páginas faltantes en `index.md`
   - comprobar que el `Total pages` del índice coincide con el recuento real
   - usar `execute_code` si hace falta para recorrer todos los `.md`

## Salida buena

- un dossier raw con fuentes y checks vivos
- varias páginas conceptuales pequeñas y enlazadas
- `index.md` actualizado
- `log.md` actualizado
- verificación final sin broken links ni incoherencias de taxonomy/index

## Anti-patrones

- reescribir la wiki a ciegas sin leer `SCHEMA.md` / `index.md` / `log.md`
- mezclar hechos documentados con suposiciones
- fiarte solo de una página vieja de la wiki si el código local dice otra cosa
- dejar tags nuevos sin añadirlos a la taxonomía
- dejar wikilinks a páginas que no existen
- actualizar páginas sin tocar índice y log
- confundir memoria integrada con session search o con provider externo

## Definición de “hecho”

El trabajo está realmente hecho cuando:
- la investigación cruza docs + código + config/estado vivo si aplica
- las páginas nuevas o actualizadas están enfocadas y no duplican sin necesidad
- `index.md`, `log.md` y `SCHEMA.md` quedan coherentes
- la comprobación estructural final sale limpia
