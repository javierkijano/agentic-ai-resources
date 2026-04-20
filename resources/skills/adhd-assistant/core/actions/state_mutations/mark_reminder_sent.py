# -*- coding: utf-8 -*-
def run(args: dict, ctx: dict) -> dict:
    state = ctx["state"]
    now = ctx["now"]
    rid = args.get("reminder_id")
    if rid is None:
        return {"ok": False, "error": "missing_reminder_id"}
    for r in state.get("support", {}).get("reminders", []):
        if str(r.get("id")) == str(rid):
            r["status"] = "sent"
            r["sent_at"] = now.isoformat()
            return {"ok": True}
    return {"ok": False, "error": "reminder_not_found"}
