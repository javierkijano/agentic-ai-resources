# -*- coding: utf-8 -*-
"""stdout channel — for tests and dry-run."""


def send(text: str, ctx: dict) -> dict:
    print(f"[adhd-assistant][stdout] {text}")
    return {"ok": True, "channel": "stdout"}
