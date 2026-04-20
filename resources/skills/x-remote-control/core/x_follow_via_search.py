#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

HERMES_ROOT = Path(__file__).resolve().parents[3]
TOOLS_PATH = HERMES_ROOT / "tools"
if str(TOOLS_PATH) not in sys.path:
    sys.path.insert(0, str(TOOLS_PATH))

from chrome_remote_control.remote_browser import (  # noqa: E402
    DEFAULT_CDP_ENDPOINTS,
    connect_chrome_over_cdp,
    ensure_page,
    human_click,
    human_delay,
    human_type,
    random_scroll,
)

DEFAULT_ACCOUNTS_FILE = Path(__file__).resolve().parents[1] / "data" / "default_accounts.txt"


def normalize_handle(raw: str) -> str:
    value = (raw or "").strip()
    if not value:
        return ""

    if value.startswith("https://x.com/"):
        value = value.replace("https://x.com/", "", 1)
    elif value.startswith("http://x.com/"):
        value = value.replace("http://x.com/", "", 1)

    value = value.split("?", 1)[0]
    value = value.split("/", 1)[0]
    value = value.lstrip("@").strip()

    if not value:
        return ""
    return f"@{value}"


def dedupe_preserve_order(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in values:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def load_handles(accounts_file: Path, cli_handles: list[str]) -> list[str]:
    handles = [normalize_handle(h) for h in cli_handles if normalize_handle(h)]
    if handles:
        return dedupe_preserve_order(handles)

    if not accounts_file.exists():
        raise FileNotFoundError(f"No existe archivo de cuentas: {accounts_file}")

    loaded: list[str] = []
    for line in accounts_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        handle = normalize_handle(stripped)
        if handle:
            loaded.append(handle)

    return dedupe_preserve_order(loaded)


async def click_people_tab(page) -> bool:
    candidates = [
        page.locator("a[role='tab']", has_text="People"),
        page.locator("a[role='tab']", has_text="Personas"),
        page.locator("span", has_text="People"),
        page.locator("span", has_text="Personas"),
    ]

    for locator in candidates:
        if await locator.count() == 0:
            continue
        candidate = locator.first
        try:
            await candidate.wait_for(state="visible", timeout=3500)
            await human_click(page, candidate)
            await human_delay(1000, 2200)
            return True
        except Exception:
            continue

    return False


async def follow_from_profile(page, dry_run: bool) -> tuple[str, str]:
    already_candidates = [
        page.locator("button:has-text('Following')"),
        page.locator("button:has-text('Siguiendo')"),
    ]

    for locator in already_candidates:
        if await locator.count() == 0:
            continue
        try:
            candidate = locator.first
            await candidate.wait_for(state="visible", timeout=1600)
            return "already_following", "Ya estaba siguiendo"
        except Exception:
            continue

    follow_candidates = [
        page.locator("button[data-testid$='-follow']"),
        page.locator("button:has-text('Follow')"),
        page.locator("button:has-text('Seguir')"),
    ]

    for locator in follow_candidates:
        if await locator.count() == 0:
            continue
        button = locator.first
        try:
            await button.wait_for(state="visible", timeout=3000)
            if dry_run:
                return "would_follow", "Dry-run activo"
            await human_click(page, button)
            await human_delay(1200, 2600)
            return "followed", "Clic en Follow"
        except Exception:
            continue

    return "failed", "No encontré botón Follow/Seguir"


async def ensure_search_input(page):
    candidates = [
        page.locator("[data-testid='SearchBox_Search_Input']"),
        page.locator("input[aria-label='Search query']"),
        page.locator("input[placeholder*='Search']"),
        page.locator("input[placeholder*='Buscar']"),
    ]

    for locator in candidates:
        if await locator.count() == 0:
            continue
        candidate = locator.first
        try:
            await candidate.wait_for(state="visible", timeout=2200)
            return candidate
        except Exception:
            continue

    await page.goto("https://x.com/explore")
    await human_delay(1300, 2600)

    for locator in candidates:
        if await locator.count() == 0:
            continue
        candidate = locator.first
        try:
            await candidate.wait_for(state="visible", timeout=3200)
            return candidate
        except Exception:
            continue

    raise PlaywrightTimeoutError("No encontré SearchBox")


async def follow_one(page, handle: str, dry_run: bool) -> tuple[str, str]:
    if (hash(handle) % 3) == 0:
        await random_scroll(page)

    try:
        search_input = await ensure_search_input(page)
        await human_click(page, search_input)
        await human_delay(100, 380)
        await page.keyboard.press("Control+A")
        await human_delay(40, 120)
        await page.keyboard.press("Backspace")
        await human_type(page, handle)
    except PlaywrightTimeoutError:
        await page.goto("https://x.com/explore")
        await human_delay(1200, 2200)
        await page.keyboard.press("/")
        await human_delay(140, 420)
        await page.keyboard.press("Control+A")
        await page.keyboard.press("Backspace")
        await human_type(page, handle)

    await human_delay(700, 1500)
    await page.keyboard.press("Enter")
    await human_delay(1700, 3200)

    await click_people_tab(page)

    user_candidates = [
        page.locator("[data-testid='UserCell']", has_text=handle),
        page.locator("[data-testid='UserCell']", has_text=handle.lstrip("@")),
    ]

    clicked_user = False
    for locator in user_candidates:
        if await locator.count() == 0:
            continue
        cell = locator.first
        try:
            await cell.wait_for(state="visible", timeout=5000)
            await human_click(page, cell)
            await human_delay(1900, 3800)
            clicked_user = True
            break
        except Exception:
            continue

    if not clicked_user:
        await page.goto(f"https://x.com/{handle.lstrip('@')}")
        await human_delay(1800, 3200)
        status, reason = await follow_from_profile(page, dry_run=dry_run)
        if status == "failed":
            return "failed", "No encontré resultado en People ni en fallback directo"
        return status, f"{reason} (fallback directo)"

    return await follow_from_profile(page, dry_run=dry_run)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seguir cuentas en X usando búsqueda + CDP remoto.")
    parser.add_argument("handles", nargs="*", help="Lista de @handles (opcional).")
    parser.add_argument(
        "--accounts-file",
        default=str(DEFAULT_ACCOUNTS_FILE),
        help="Archivo con cuentas (una por línea).",
    )
    parser.add_argument(
        "--cdp-url",
        action="append",
        default=[],
        help="Endpoint CDP a probar (se puede repetir).",
    )
    parser.add_argument("--limit", type=int, default=0, help="Limitar número de cuentas (0 = todas).")
    parser.add_argument("--dry-run", action="store_true", help="No pulsa Follow, solo simula recorrido.")
    return parser.parse_args()


async def run(args: argparse.Namespace) -> int:
    handles = load_handles(Path(args.accounts_file), args.handles)
    if args.limit > 0:
        handles = handles[: args.limit]

    if not handles:
        raise RuntimeError("No hay handles para procesar.")

    cdp_urls = args.cdp_url if args.cdp_url else list(DEFAULT_CDP_ENDPOINTS)

    followed: list[str] = []
    already: list[str] = []
    dry_run_hits: list[str] = []
    failed: list[tuple[str, str]] = []

    async with async_playwright() as playwright:
        browser, endpoint = await connect_chrome_over_cdp(playwright, cdp_urls)
        page = await ensure_page(browser)

        print(f"CDP conectado: {endpoint}")
        print(f"Cuentas objetivo: {len(handles)}")

        await page.goto("https://x.com/home")
        await human_delay(2500, 4500)

        for idx, handle in enumerate(handles, start=1):
            print(f"[{idx}/{len(handles)}] {handle}")
            try:
                status, reason = await follow_one(page, handle, dry_run=args.dry_run)
            except Exception as exc:
                status, reason = "failed", f"Excepción: {exc}"

            if status == "followed":
                followed.append(handle)
            elif status == "already_following":
                already.append(handle)
            elif status == "would_follow":
                dry_run_hits.append(handle)
            else:
                failed.append((handle, reason))

            print(f"  -> {status}: {reason}")
            await human_delay(1300, 2600)
            await page.goto("https://x.com/home")
            await human_delay(1800, 3200)

    print("\nResumen")
    print(f"- Followed: {len(followed)}")
    print(f"- Already following: {len(already)}")
    if args.dry_run:
        print(f"- Would follow (dry-run): {len(dry_run_hits)}")
    print(f"- Failed: {len(failed)}")

    if failed:
        print("\nFallos:")
        for handle, reason in failed:
            print(f"- {handle}: {reason}")

    return 0 if not failed else 2


def main() -> int:
    args = parse_args()
    try:
        return asyncio.run(run(args))
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
