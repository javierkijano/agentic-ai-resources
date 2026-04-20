from __future__ import annotations

import asyncio
import random
from typing import Iterable, Sequence

DEFAULT_CDP_ENDPOINTS: tuple[str, ...] = (
    "http://127.0.0.1:9222",
    "http://localhost:9222",
)


async def connect_chrome_over_cdp(playwright, cdp_urls: Sequence[str] | None = None, timeout_ms: int = 5000):
    """Try one or more CDP endpoints and return (browser, endpoint)."""
    urls = list(cdp_urls or DEFAULT_CDP_ENDPOINTS)
    errors: list[str] = []

    for url in urls:
        try:
            browser = await playwright.chromium.connect_over_cdp(url, timeout=timeout_ms)
            return browser, url
        except Exception as exc:  # pragma: no cover - network/runtime dependent
            errors.append(f"{url}: {exc}")

    details = " | ".join(errors) if errors else "sin detalle"
    raise RuntimeError(
        "No se pudo conectar a Chrome por CDP. "
        "Verifica puerto 9222 y user-data-dir no por defecto. "
        f"Intentos: {details}"
    )


async def ensure_page(browser):
    """Return a usable page from the default CDP context."""
    if not browser.contexts:
        raise RuntimeError("Chrome CDP no expone contextos; revisa la sesión de depuración.")

    context = browser.contexts[0]
    if context.pages:
        return context.pages[0]
    return await context.new_page()


async def human_delay(min_ms: int = 350, max_ms: int = 1300):
    """Random delay in milliseconds."""
    low, high = sorted((min_ms, max_ms))
    await asyncio.sleep(random.uniform(low, high) / 1000.0)


async def human_type(page, text: str, min_key_ms: int = 45, max_key_ms: int = 220, pause_chance: float = 0.1):
    """Type text key-by-key with variable speed and occasional pauses."""
    for char in text:
        await page.keyboard.type(char, delay=random.randint(min_key_ms, max_key_ms))
        if random.random() < pause_chance:
            await human_delay(180, 650)


async def human_click(page, locator):
    """Move mouse to a random point in the element and click with jitter."""
    await locator.scroll_into_view_if_needed()
    box = await locator.bounding_box()

    if not box:
        await locator.click(timeout=3000)
        return

    target_x = box["x"] + (box["width"] * random.uniform(0.22, 0.78))
    target_y = box["y"] + (box["height"] * random.uniform(0.22, 0.78))

    steps = random.randint(6, 18)
    await page.mouse.move(target_x, target_y, steps=steps)
    await human_delay(60, 280)
    await page.mouse.down()
    await human_delay(35, 120)
    await page.mouse.up()


async def random_scroll(page, min_delta: int = -280, max_delta: int = 700):
    """Small random wheel movement to mimic reading behavior."""
    low, high = sorted((min_delta, max_delta))
    delta = random.randint(low, high)
    if -40 < delta < 40:
        delta = 120 if delta >= 0 else -120
    await page.mouse.wheel(0, delta)
    await human_delay(700, 2200)
