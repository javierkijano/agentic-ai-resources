#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import sys
from collections import OrderedDict
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
    human_delay,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Listar cuentas seguidas (visibles) en X via CDP.")
    parser.add_argument("username", help="Usuario objetivo sin @ (ej: reivajano)")
    parser.add_argument("--scroll-rounds", type=int, default=10, help="Número máximo de rondas de scroll.")
    parser.add_argument("--cdp-url", action="append", default=[], help="Endpoint CDP (se puede repetir).")
    return parser.parse_args()


def normalize_username(value: str) -> str:
    user = value.strip().lstrip("@")
    user = user.split("?", 1)[0]
    user = user.split("/", 1)[0]
    return user


async def extract_visible_handles(page) -> list[str]:
    handles = OrderedDict()
    cards = page.locator("[data-testid='UserCell']")
    card_count = await cards.count()

    for i in range(card_count):
        card = cards.nth(i)
        links = card.locator("a[href^='/']")
        link_count = await links.count()

        for j in range(link_count):
            href = await links.nth(j).get_attribute("href")
            if not href:
                continue

            username = href.split("?", 1)[0].strip("/")
            if not username or "/" in username:
                continue
            if username in {"i", "home", "explore", "notifications", "messages", "search"}:
                continue

            handles[f"@{username}"] = None
            break

    return list(handles.keys())


async def run(args: argparse.Namespace) -> int:
    username = normalize_username(args.username)
    if not username:
        raise RuntimeError("username inválido")

    cdp_urls = args.cdp_url if args.cdp_url else list(DEFAULT_CDP_ENDPOINTS)

    discovered = OrderedDict()
    stable_rounds = 0

    async with async_playwright() as playwright:
        browser, endpoint = await connect_chrome_over_cdp(playwright, cdp_urls)
        page = await ensure_page(browser)

        url = f"https://x.com/{username}/following"
        await page.goto(url)
        await human_delay(2500, 4200)

        print(f"CDP conectado: {endpoint}")
        print(f"Leyendo: {url}")

        for _ in range(max(1, args.scroll_rounds)):
            current = await extract_visible_handles(page)
            before = len(discovered)
            for handle in current:
                discovered[handle] = None

            if len(discovered) == before:
                stable_rounds += 1
            else:
                stable_rounds = 0

            if stable_rounds >= 3:
                break

            await page.mouse.wheel(0, 1200)
            await human_delay(900, 1800)

    print(f"\nTotal visibles: {len(discovered)}")
    for handle in discovered.keys():
        print(handle)

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
