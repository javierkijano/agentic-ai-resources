---
name: linkedin
description: Investigación web + estrategia de contenido para LinkedIn con modo guiado paso a paso, 3 propuestas con hashtags, idioma en inglés por configuración y memoria persistente con calendario objetivo por temas.
version: 2.1.0
author: Javier + Hermes
license: MIT
platforms: [linux, macos]
prerequisites:
  commands: [npm, linkedin, python3]
  env_vars: [LINKEDIN_LI_AT, LINKEDIN_JSESSIONID]
metadata:
  hermes:
    tags: [linkedin, social-media, research, content-strategy, memory, engagement, calendar]
    homepage: https://github.com/bcharleson/linkedincli
---

# LinkedIn — research + ideación + publicación + memoria + calendario

Esta skill combina 5 capacidades:

1) investigar en internet un tema concreto para un ámbito específico,
2) proponer 3 ideas de publicación con potencial de engagement,
3) trabajar en modo guiado paso a paso,
4) guardar memoria de intereses/publicaciones/feedback,
5) planificar un calendario objetivo por temas para aprender qué toca en cada momento.

## Dependencias

### LinkedIn CLI

```bash
npm install -g @bcharleson/linkedincli --no-fund --no-audit
linkedin --help
```

### Script de memoria (incluido en la skill)

```bash
python3 {{AGENTIC_RESOURCES}}/hermes/skills/linkedin/scripts/linkedin_memory.py --help
```

## Autenticación LinkedIn (cookies)

Necesitas cookies de sesión activas:
- `li_at`
- `JSESSIONID` (incluyendo prefijo tipo `ajax:...`)

```bash
linkedin login --li-at "<TU_LI_AT>" --jsessionid "<TU_JSESSIONID>"
linkedin status --verify
```

Sesión guardada en:
`~/.linkedin-cli/config.json`

## Configuración de idioma (obligatoria)

La skill incorpora:
- `preferred_language`
- `suggested_language`

Ambas están restringidas a inglés (`en`).

```bash
python3 {{AGENTIC_RESOURCES}}/hermes/skills/linkedin/scripts/linkedin_memory.py init \
  --profile "javier-linkedin" --preferred-language en --suggested-language en

python3 {{AGENTIC_RESOURCES}}/hermes/skills/linkedin/scripts/linkedin_memory.py set-config \
  --profile "javier-linkedin" --preferred-language en --suggested-language en
```

## Modos de ejecución

### Modo guiado (paso a paso)

Flujo obligatorio:

1. Cargar memoria y configuración del perfil (incluye idioma y mix de contenido).
2. Definir briefing: ámbito, tema, objetivo, audiencia y tono.
3. Investigar internet (fuentes recientes y relevantes).
4. Sintetizar hallazgos accionables.
5. Proponer exactamente 3 publicaciones.
6. Elegir/editar una propuesta.
7. (Opcional) Publicar en LinkedIn.
8. Guardar feedback y actualizar calendario/learning.

### Modo directo

Cuando el usuario ya trae tema y copy casi cerrados:

1. Validar sesión.
2. Generar 3 propuestas rápidas (o 1 si se pide).
3. Publicar.
4. Registrar feedback.

## Protocolo de investigación web (obligatorio)

1) Búsqueda web orientada al ámbito.
- mínimo 5 resultados candidatos
- priorizar datos, informes, benchmarks y noticias recientes

2) Extracción de fuentes.
- mínimo 3 fuentes
- registrar URL de cada evidencia usada

3) Síntesis útil.
- qué cambia
- implicación práctica
- oportunidad de opinión diferenciada

## Reglas de contenido (nuevas)

1) Muchas publicaciones deben ser contenido compartido (`news-share` o `video-share`).
- se controla con `shared_content_target_ratio` en configuración
- recomendado base: 0.65

2) Toda publicación compartida debe incluir reflexión propia.
- se controla con `reflection_required_for_shared=true`

3) Hashtags obligatorios.
- mínimo/máximo configurable (`min_hashtags`, `max_hashtags`)
- si no se pasan, el script los autogenera

4) Idioma de publicación: inglés (`en`).

## Salida estándar: 3 propuestas

Siempre devolver 3 propuestas con este formato:

- `proposal_id`
- `title` (EN)
- `hook` (EN)
- `angle`
- `draft` (EN)
- `content_type` (`insight` | `news-share` | `video-share`)
- `reflection` (obligatoria si es shared)
- `why_it_can_get_engagement`
- `target_audience`
- `cta` (EN)
- `hashtags` (3-8)
- `sources` (2-4 URLs)

## Memoria persistente

La memoria vive en:
`~/.hermes/linkedin/memory.json`

Por perfil:
- `settings` (idioma, mix, calendario)
- `interests`
- `theme_goals`
- `calendar_entries`
- `publications`
- `feedback`
- `learning.notes`

Template:
`{{AGENTIC_RESOURCES}}/hermes/skills/linkedin/data/memory.template.json`

## Comandos de memoria y configuración

### Ver/editar configuración

```bash
python3 {{AGENTIC_RESOURCES}}/hermes/skills/linkedin/scripts/linkedin_memory.py show-config --profile "javier-linkedin"

python3 {{AGENTIC_RESOURCES}}/hermes/skills/linkedin/scripts/linkedin_memory.py set-config \
  --profile "javier-linkedin" \
  --shared-content-target-ratio 0.65 \
  --reflection-required-for-shared true \
  --min-hashtags 4 --max-hashtags 8 \
  --objective-posts-per-week 3 \
  --planning-horizon-weeks 4 \
  --preferred-weekdays monday,wednesday,friday
```

### Registrar interés

```bash
python3 {{AGENTIC_RESOURCES}}/hermes/skills/linkedin/scripts/linkedin_memory.py add-interest \
  --profile "javier-linkedin" \
  --domain "travel-tech" \
  --topic "dynamic pricing with AI" \
  --notes "Practical angle with business impact"
```

### Registrar objetivo por tema (calendario)

```bash
python3 {{AGENTIC_RESOURCES}}/hermes/skills/linkedin/scripts/linkedin_memory.py add-theme-goal \
  --profile "javier-linkedin" \
  --domain "travel-tech" \
  --theme "pricing trust and fairness" \
  --posts-per-month 5 \
  --priority 5 \
  --preferred-content-types news-share,video-share,insight
```

### Generar calendario objetivo

```bash
python3 {{AGENTIC_RESOURCES}}/hermes/skills/linkedin/scripts/linkedin_memory.py generate-calendar \
  --profile "javier-linkedin" \
  --weeks 4 \
  --objective-posts-per-week 3 \
  --replace-planned
```

### Ver calendario

```bash
python3 {{AGENTIC_RESOURCES}}/hermes/skills/linkedin/scripts/linkedin_memory.py calendar \
  --profile "javier-linkedin" --days 45 --limit 30
```

### Guardar publicación

```bash
python3 {{AGENTIC_RESOURCES}}/hermes/skills/linkedin/scripts/linkedin_memory.py add-publication \
  --profile "javier-linkedin" \
  --domain "travel-tech" \
  --topic "pricing trust and fairness" \
  --title "AI pricing without breaking customer trust" \
  --hook "The main AI pricing risk is not math. It's perceived unfairness." \
  --angle "strategy" \
  --draft "Post text in English..." \
  --content-type news-share \
  --shared-url "https://example.com/news" \
  --reflection "My take: transparency and guardrails are non-negotiable." \
  --sources "https://example.com/news,https://example.com/report" \
  --hashtags "#dynamicpricing,#airlineretailing,#ai,#traveltech" \
  --language en \
  --status proposed
```

### Guardar feedback

```bash
python3 {{AGENTIC_RESOURCES}}/hermes/skills/linkedin/scripts/linkedin_memory.py add-feedback \
  --profile "javier-linkedin" \
  --publication-id "pub_..." \
  --score 4 \
  --likes 58 --comments 12 --shares 4 --saves 15 \
  --notes "Strong hook; keep short opening" \
  --preference-note "News-share + strong reflection performs well" \
  --status published
```

### Resumen operativo

```bash
python3 {{AGENTIC_RESOURCES}}/hermes/skills/linkedin/scripts/linkedin_memory.py summary \
  --profile "javier-linkedin" --top 5
```

El resumen devuelve:
- top topics
- tracking del mix de contenido
- cobertura de hashtags
- próximos huecos del calendario

## Publicación en LinkedIn

```bash
linkedin status --verify
linkedin posts create --text "Final English post" --visibility anyone
```

## Flujo operativo recomendado para Hermes

1. `linkedin status --verify`
2. `linkedin_memory.py show-config --profile <perfil>`
3. `linkedin_memory.py summary --profile <perfil>`
4. Investigación web
5. Proponer 3 publicaciones en EN con hashtags
6. Guardar propuestas (`add-publication`)
7. (Opcional) publicar con `linkedin posts create`
8. Guardar feedback (`add-feedback`)
9. Regenerar calendario si cambia la estrategia (`generate-calendar`)

## Convención de modo guiado

Paso 1/5 — Briefing
- ámbito + tema + objetivo + audiencia

Paso 2/5 — Investigación
- fuentes + insights

Paso 3/5 — Propuestas
- 3 opciones exactas en EN
- con hashtags y tipo de contenido

Paso 4/5 — Selección y ajuste
- pulido final

Paso 5/5 — Publicación y aprendizaje
- publicación + feedback + actualización de memoria/calendario

## Pitfalls

- Cookies caducadas: renovar con `linkedin login`.
- No publicar shared content sin reflexión.
- No omitir hashtags.
- No salir del inglés configurado para los posts.
- No generar ideas sin fuentes.
- No saltarse feedback post-publicación: sin feedback no hay aprendizaje real.
