---
name: chrome-remote-browser-control
description: Controlar un navegador Chrome local vía CDP (remote debugging) con Playwright, incluyendo helpers de comportamiento humano y diagnóstico rápido.
version: 1.0.0
author: Javier + Hermes
license: MIT
platforms: [linux]
prerequisites:
  commands: [google-chrome, uv, ss, curl]
metadata:
  hermes:
    tags: [chrome, cdp, playwright, browser-automation, remote-debugging]
---

# Chrome remote browser control

Skill base para operar Chrome abierto por el usuario usando CDP (`--remote-debugging-port=9222`).

## Cuándo usar

- Automatización en una sesión ya autenticada del navegador.
- Navegación asistida con comportamiento menos mecánico.
- Diagnóstico cuando `connect_over_cdp` falla.

## Arranque correcto de Chrome (obligatorio)

Chrome exige un perfil no por defecto para CDP:

```bash
google-chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome_cdp_profile"
```

Sin `--user-data-dir`, CDP puede quedar inactivo aunque Chrome esté abierto.

## Verificación rápida

```bash
ss -tulpn | grep 9222
curl -s http://127.0.0.1:9222/json/version
```

## Probe de conexión

```bash
uv run --with playwright python {{AGENTIC_RESOURCES}}/hermes/skills/chrome-remote-browser-control/scripts/cdp_probe.py
```

Opcional:

```bash
uv run --with playwright python {{AGENTIC_RESOURCES}}/hermes/skills/chrome-remote-browser-control/scripts/cdp_probe.py --goto https://x.com/home
```

## Implementación reusable

Helpers disponibles en:

`{{AGENTIC_RESOURCES}}/hermes/tools/chrome_remote_control/remote_browser.py`

Funciones clave:
- `connect_chrome_over_cdp(...)`
- `ensure_page(...)`
- `human_delay(...)`
- `human_type(...)`
- `human_click(...)`
- `random_scroll(...)`

## Troubleshooting

Ver `references/troubleshooting.md`.
