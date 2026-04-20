---
name: telegram-inline-keyboard
description: Send Telegram messages with inline keyboard buttons via Bot API curl. Use for task nudges, confirmations, and interactive prompts in Telegram groups/chats.
tags: [telegram, bot-api, inline-keyboard, nudges, curl]
---

# Telegram Inline Keyboard Messages

## When to use
- Sending interactive messages with buttons to Telegram chats
- Task nudge system ("mosca cojonera") with Hecho/Posponer/Ver detalles
- Any message requiring user action via inline buttons

## Prerequisites
- Bot token: source from `~/.hermes/.env` (TELEGRAM_BOT_TOKEN)
- Chat must have the bot added and /start initiated
- Chat ID must be in config.yaml free_response_chats for Hermes responses

## Send message with inline keyboard

**CRITICAL: Use form-urlencoded with separate -d params, NOT -H "Content-Type: application/json" with a JSON body.**
Passing a JSON body with `-d '{...}'` without explicit Content-Type causes Telegram to return
"Bad Request: message text is empty" because curl defaults to form-urlencoded and Telegram
can't parse the JSON blob as form fields. The fix: use separate `-d` for text fields and
`--data-urlencode` for the reply_markup JSON.

```bash
source ~/.hermes/.env && curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=CHAT_ID_HERE" \
  -d "text=MESSAGE_TEXT_HERE" \
  --data-urlencode 'reply_markup={"inline_keyboard":[[{"text":"✅ Hecho","callback_data":"done"},{"text":"⏰ Posponer","callback_data":"postpone"},{"text":"📋 Ver detalles","callback_data":"details"}]]}'
```

## Simple yes/no buttons

```bash
source ~/.hermes/.env && curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=CHAT_ID_HERE" \
  -d "text=Si o No?" \
  --data-urlencode 'reply_markup={"inline_keyboard":[[{"text":"Si","callback_data":"yes"},{"text":"No","callback_data":"no"}]]}'
```

## Plain text (no buttons)

```bash
source ~/.hermes/.env && curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=CHAT_ID_HERE" \
  -d "text=Hello world"
```

## Multiple rows of buttons

Use `--data-urlencode` with nested arrays:
```bash
--data-urlencode 'reply_markup={"inline_keyboard":[[{"text":"Row 1 Btn 1","callback_data":"r1b1"},{"text":"Row 1 Btn 2","callback_data":"r1b2"}],[{"text":"Row 2 Btn 1","callback_data":"r2b1"}]]}'
```

## Key chat IDs (jq-hermes-01 prefix)
- skills: -5274297793
- psicologia: -5104231326
- tareas: -5202280877
- ideas-negocios: -4922895569
- politica: -5181255693
- ideas-hijos: -5163577453
- edreams: -5225650190

## Response check
- Success: `{"ok": true, "result": {"message_id": N, ...}}`
- Failure: `{"ok": false, "description": "error message"}`

## Pitfalls
1. Token is in ~/.hermes/.env — always `source` it first, don't search elsewhere
2. **DO NOT pass JSON body with `-d '{...}'` alone** — curl sends it as form-urlencoded by default and Telegram returns "message text is empty". Use separate `-d` per field + `--data-urlencode` for reply_markup (see examples above). This was the #1 source of failures.
3. Don't expose token in memory or logs
4. Bot must be admin or have send_messages permission in groups
5. callback_data max 64 bytes
6. Avoid special characters (accents like í, ñ, emojis) in the `-d "text=..."` param if you get encoding errors — use `--data-urlencode "text=..."` instead for Unicode text
