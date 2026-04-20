# -*- coding: utf-8 -*-
def run(args: dict, ctx: dict) -> dict:
    state = ctx["state"]
    now = ctx["now"]
    task_id = args.get("task_id")
    if task_id is None:
        return {"ok": False, "error": "missing_task_id"}
    for t in state.get("commitments", {}).get("tasks", []):
        if str(t.get("id")) == str(task_id):
            t["last_nudged_at"] = now.isoformat()
            t["nudge_count"] = int(t.get("nudge_count", 0)) + 1
            return {"ok": True}
    return {"ok": False, "error": "task_not_found"}
