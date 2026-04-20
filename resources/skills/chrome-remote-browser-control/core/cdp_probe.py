#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright

HERMES_ROOT = Path(__file__).resolve().parents[3]
TOOLS_PATH = HERMES_ROOT / "tools"
if str(TOOLS_PATH) not in sys.path:
    sys.path.insert(0, str(TOOLS_PATH))

from chrome_remote_control.remote_browser import (  # noqa: E402
    DEFAULT_CDP_ENDPOINTS,
    connect_chrome_over_cdp,
    ensure_page,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diagnóstico de conexión CDP a Chrome.")
    parser.add_argument(
        "--cdp-url",
        action="append",
        default=[],
        help="Endpoint CDP a probar (se puede repetir). Ej: http://127.0.0.1:9222",
    )
    parser.add_argument(
        "--goto",
        default="",
        help="URL opcional para abrir tras conectar.",
    )
    return parser.parse_args()


async def run(args: argparse.Namespace) -> int:
    cdp_urls = args.cdp_url if args.cdp_url else list(DEFAULT_CDP_ENDPOINTS)

    async with async_playwright() as playwright:
        browser, endpoint = await connect_chrome_over_cdp(playwright, cdp_urls)
        page = await ensure_page(browser)

        if args.goto:
            await page.goto(args.goto)

        title = await page.title()
        page_count = sum(len(ctx.pages) for ctx in browser.contexts)

        print(f"CDP OK: {endpoint}")
        print(f"Contextos: {len(browser.contexts)} | Páginas: {page_count}")
        print(f"URL activa: {page.url}")
        print(f"Título: {title}")

    return 0


def main() -> int:
    args = parse_args()
    try:
        return asyncio.run(run(args))
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
