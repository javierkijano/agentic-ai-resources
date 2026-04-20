# -*- coding: utf-8 -*-
"""Append entry to the hindsight queue (JSONL).

The actual call to hindsight_retain happens OUT of this script: a separate flush
script drains the queue with the Hindsight client.
"""

import fcntl
import json
import os


def run(args: dict, ctx: dict) -> dict:
    qpath = ctx.get("hindsight_queue_path")
    if not qpath:
        return {"ok": False, "error": "no_queue_path"}

    os.makedirs(os.path.dirname(qpath), exist_ok=True)
    entry = {
        "at": ctx["now"].isoformat(),
        "context": args.get("context", "adhd-assistant:event"),
        "content": args.get("content", ""),
        "tags": args.get("tags", ["adhd-assistant"]),
    }

    with open(qpath, "a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            handle.seek(0, os.SEEK_END)
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    return {"ok": True}
