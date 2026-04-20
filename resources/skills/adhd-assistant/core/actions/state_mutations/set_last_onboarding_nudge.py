# -*- coding: utf-8 -*-
def run(args: dict, ctx: dict) -> dict:
    state = ctx["state"]
    now = ctx["now"]
    state.setdefault("history", {})["last_onboarding_nudge_at"] = now.isoformat()
    return {"ok": True}
