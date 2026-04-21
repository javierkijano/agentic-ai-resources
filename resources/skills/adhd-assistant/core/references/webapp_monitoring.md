# ADHD Assistant Web Monitor

## Objetivo

Añadir una capa web de observabilidad para `adhd-assistant` sin romper el motor
proactivo existente.

Características base:
- lectura de `state.json`
- lectura de `config.yaml` (redactando secretos)
- estado de ficheros runtime
- resumen de métricas (tasks/appointments/reminders)
- últimos ticks (`logs/tick-*.jsonl`)
- cola `hindsight_queue.jsonl`
- catálogo de políticas/modos/coaching activos

## Layout

```text
webapp/
├── app.py                     # FastAPI routes + HTML entrypoints
├── services/
│   └── runtime_monitor.py     # lógica de monitorización (read-only)
├── templates/
│   ├── index.html             # dashboard
│   └── calendar.html          # mockup de calendario local
└── static/
    ├── styles.css
    └── dashboard.js
```

## Run

Desde la carpeta de la skill:

```bash
cd {{AGENTIC_RESOURCES}}/hermes/skills/adhd-assistant
python3 -m webapp.app
```

Abrir:

```text
http://127.0.0.1:8765
```

Variables opcionales:

- `HERMES_HOME` (por defecto `~/.hermes`)
- `ADHD_WEBAPP_HOST` (default `127.0.0.1`)
- `ADHD_WEBAPP_PORT` (default `8765`)
- `ADHD_WEBAPP_RELOAD` (`1` para auto-reload)

## API

### HTML
- `GET /`
- `GET /calendar?days=14`

### JSON
- `GET /api/health`
- `GET /api/summary`
- `GET /api/catalog`
- `GET /api/files`
- `GET /api/logs?limit=...`
- `GET /api/hindsight-queue?limit=...`
- `GET /api/state`
- `GET /api/config`
- `GET /api/calendar-mockup?days=14`
- `GET /api/dashboard`

## Extensibilidad

### 1) Nueva métrica de resumen

Añadir función en `RuntimeMonitor` y exponerla dentro de `build_summary()`.

### 2) Nueva fuente de observabilidad

Agregar reader en `RuntimeMonitor` (ej. métricas de un nuevo canal) y endpoint en
`app.py`.

### 3) Nueva visualización

Editar `templates/index.html` + `static/dashboard.js` para pintar la sección.

## Guardrail

La implementación actual es **read-only**: no muta estado ni dispara acciones.
Esto permite usarla como capa de monitorización segura para evolución futura.
