---
name: x-remote-control
description: Gestionar X/Twitter desde una sesión real de Chrome usando CDP + Playwright (seguir cuentas, leer following visible y automatizar búsqueda con patrones humanos).
version: 1.0.0
author: Javier + Hermes
license: MIT
platforms: [linux]
prerequisites:
  commands: [google-chrome, uv]
metadata:
  hermes:
    tags: [x, twitter, chrome, cdp, playwright, social-media]
---

# X remote control (Chrome CDP)

Automatización de X sobre navegador real autenticado (sin API de follow).

## Dependencia base

Esta skill usa helpers de:

`/home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/tools/chrome_remote_control/remote_browser.py`

## Preparación

1) Arranca Chrome con CDP y perfil no-default:

```bash
google-chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome_cdp_profile"
```

2) Inicia sesión en `https://x.com` en esa misma ventana.

## Scripts

### 1) Seguir cuentas vía búsqueda (modo humano)

```bash
uv run --with playwright python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/x-remote-control/scripts/x_follow_via_search.py
```

Con lista custom:

```bash
uv run --with playwright python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/x-remote-control/scripts/x_follow_via_search.py @POTUS @JMilei
```

Usando archivo propio:

```bash
uv run --with playwright python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/x-remote-control/scripts/x_follow_via_search.py --accounts-file /ruta/accounts.txt
```

Dry-run (sin clicar Follow):

```bash
uv run --with playwright python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/x-remote-control/scripts/x_follow_via_search.py --dry-run
```

### 2) Listar cuentas seguidas (visibles)

```bash
uv run --with playwright python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/x-remote-control/scripts/x_list_following.py reivajano
```

## Datos por defecto

Archivo de handles por defecto:

`/home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/x-remote-control/data/default_accounts.txt`

## Notas

- No usa endpoint de follow de API oficial de X.
- Los selectores de X cambian; mantener fallback por texto (`Follow/Seguir`, `People/Personas`) y fallback final por URL directa del perfil.
- Mantener pausas variables para evitar patrón rígido.
