# -*- coding: utf-8 -*-
"""Queue a full-state snapshot for hindsight."""
import json
import os


def run(args: dict, ctx: dict) -> dict:
    qpath = ctx.get("hindsight_queue_path")
    if not qpath:
        return {"ok": False, "error": "no_queue_path"}
    os.makedirs(os.path.dirname(qpath), exist_ok=True)
    entry = {
        "at": ctx["now"].isoformat(),
        "context": "adhd-assistant:state-snapshot",
        "content": json.dumps(ctx["state"], ensure_ascii=False),
        "tags": ["adhd-assistant", "state-snapshot"],
    }
    with open(qpath, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return {"ok": True}
