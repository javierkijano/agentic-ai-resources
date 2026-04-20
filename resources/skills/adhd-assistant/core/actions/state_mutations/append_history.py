# -*- coding: utf-8 -*-
def run(args: dict, ctx: dict) -> dict:
    state = ctx["state"]
    now = ctx["now"]
    history = state.setdefault("history", {})
    recent = history.setdefault("recent_events", [])
    recent.append({
        "at": now.isoformat(),
        "kind": args.get("kind", "event"),
        "summary": args.get("summary", ""),
    })
    # trim
    if len(recent) > 200:
        del recent[:-200]
    history["last_proactive_message_at"] = now.isoformat()
    return {"ok": True}
