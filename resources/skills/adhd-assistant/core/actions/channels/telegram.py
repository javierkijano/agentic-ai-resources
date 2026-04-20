# -*- coding: utf-8 -*-
"""Telegram channel using Bot API sendMessage via urllib (no external deps)."""
import json
import os
import urllib.parse
import urllib.request

HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
ENV_PATH = os.path.join(HERMES_HOME, ".env")


def _load_token_from_env_file(var_name: str) -> str:
    if not os.path.exists(ENV_PATH):
        return ""
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == var_name:
                return v.strip().strip('"').strip("'")
    return ""


def send(text: str, ctx: dict) -> dict:
    cfg = ctx.get("config", {})
    delivery = cfg.get("delivery", {}) or {}
    tg = delivery.get("telegram", {}) or {}
    token_env = tg.get("token_env", "TELEGRAM_BOT_TOKEN")
    token = os.environ.get(token_env) or _load_token_from_env_file(token_env)
    chat_id = tg.get("chat_id")

    if not token:
        return {"ok": False, "error": "missing_telegram_token"}
    if not chat_id:
        return {"ok": False, "error": "missing_chat_id"}

    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": "true",
    }).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage", data=data
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            if payload.get("ok"):
                return {"ok": True, "channel": "telegram", "message_id": payload.get("result", {}).get("message_id")}
            return {"ok": False, "error": payload.get("description", "tg_api_error")}
    except Exception as e:  # pragma: no cover
        return {"ok": False, "error": f"tg_exception:{e}"}
