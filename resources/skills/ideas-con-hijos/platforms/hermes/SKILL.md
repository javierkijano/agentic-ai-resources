---
name: ideas-con-hijos
description: Catálogo práctico de actividades para hacer con hijos. Sirve tanto para responder por texto como para navegar una app sencilla con contenido mixto: original, adaptado y externo.
version: 0.1.0
author: Javier + Hermes
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [familia, hijos, actividades, manualidades, experiments, product, app]
---

# Ideas con hijos

Skill canónica para este tema. Su objetivo no es “inspirar” sin más, sino **resolver rápido** la pregunta real:

> “¿Qué puedo hacer hoy con los niños, con el tiempo y materiales que tengo, sin pensar demasiado?”

## Cuándo usar

Usa esta skill cuando Javier pida:
- ideas para hacer con hijos
- manualidades o experimentos en casa
- algo para lluvia, antes de cenar o sin pantallas
- una app o interfaz gráfica para explorar este catálogo
- revisar, ampliar o reestructurar el sistema de actividades familiares

## Principios

1. **Utilidad antes que branding**
   - Responder con actividades accionables.
   - Menos discurso, más edad/tiempo/materiales/preparación.

2. **Procedencia explícita siempre**
   Cada actividad del catálogo debe indicar una de estas procedencias:
   - `internal_original` → idea propia
   - `adapted_from_source` → adaptada de una fuente externa
   - `external_reference` → la explicación completa vive fuera

3. **No fingir contenido propio cuando no lo es**
   Si algo está adaptado o vive fuera, se dice.

4. **Reducir carga mental**
   En texto, devolver pocas opciones y bien filtradas.
   En app, priorizar filtros prácticos y fichas escaneables.

## Activos principales

- Catálogo local: `data/activities.json`
- CLI de texto: `scripts/catalog_cli.py`
- App gráfica: `webapp/app.py`

## Flujo recomendado en modo texto

### 1) Buscar primero en catálogo local

```bash
cd /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/ideas-con-hijos
python3 scripts/catalog_cli.py search --query "cartón 10 min"
python3 scripts/catalog_cli.py search --context antes-de-cenar --max-duration 15
python3 scripts/catalog_cli.py show --slug mision-laser-en-el-pasillo
```

### 2) Formato de respuesta recomendado

Cuando haya buen match, contestar con **máximo 3 opciones** y para cada una dar:
- edad
- tiempo
- materiales
- nivel de preparación / lío si importa
- por qué encaja ahora
- procedencia (`Original`, `Adaptada`, `Fuente externa`)

### 3) Si no hay match suficiente

Permitir tres salidas:
- **crear una idea original** y marcarla como tal
- **adaptar una fuente externa** y citarla
- **pasar una referencia externa** si la explicación ya está bien hecha fuera

## Flujo recomendado en modo app

La app es la capa gráfica de esta skill, no un producto separado.

Arranque:

```bash
cd /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/ideas-con-hijos
python3 -m webapp.app
```

Abrir:

```text
http://127.0.0.1:8766
```

### Qué debe mostrar la app

- búsqueda por texto
- filtros por tipo, contexto, origen, edad y duración
- tarjetas rápidas con metadata visible
- ficha lateral con pasos, variantes y fuente
- distinción visual entre:
  - original
  - adaptada
  - externa

## Reglas editoriales

- Evitar copy inflado o “landing page”.
- Preferir contextos reales:
  - antes de cenar
  - día de lluvia
  - bajar revoluciones
  - con lo que ya tienes
- Si una actividad es externa, conservar URL rastreable.
- Si una actividad es adaptada, resumirla con honestidad y citar la fuente.

## Validación mínima

```bash
cd /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/ideas-con-hijos
python3 scripts/catalog_cli.py stats
python3 scripts/catalog_cli.py search --query "linterna"
python3 -m tests.test_catalog
python3 -m tests.test_webapp
```

## Qué queda preparado con esta versión

- skill textual reutilizable
- catálogo inicial con mezcla de contenido propio + adaptado + externo
- app sencilla para exploración gráfica
- base para ampliar contenido real sin rehacer la estructura
