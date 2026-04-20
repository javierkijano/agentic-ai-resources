"""Chrome CDP remote-control helpers for Hermes skills."""

from .remote_browser import (
    DEFAULT_CDP_ENDPOINTS,
    connect_chrome_over_cdp,
    ensure_page,
    human_click,
    human_delay,
    human_type,
    random_scroll,
)

__all__ = [
    "DEFAULT_CDP_ENDPOINTS",
    "connect_chrome_over_cdp",
    "ensure_page",
    "human_click",
    "human_delay",
    "human_type",
    "random_scroll",
]
