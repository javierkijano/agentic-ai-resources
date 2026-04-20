# -*- coding: utf-8 -*-
def run(args: dict, ctx: dict) -> dict:
    state = ctx["state"]
    now = ctx["now"]
    state.setdefault("history", {})["last_daily_review_date"] = now.date().isoformat()
    return {"ok": True}
