#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import uuid
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

RUNTIME_DIR = Path(os.path.expanduser("~/.hermes/linkedin"))
MEMORY_FILE = RUNTIME_DIR / "memory.json"

ENGLISH_ALIASES = {"en", "english", "en-us", "en-gb"}
WEEKDAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]
WEEKDAY_ALIASES = {
    "mon": "monday",
    "tue": "tuesday",
    "wed": "wednesday",
    "thu": "thursday",
    "fri": "friday",
    "sat": "saturday",
    "sun": "sunday",
}
SHARED_CONTENT_TYPES = {"news-share", "video-share"}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def normalize_language(value: str, field_name: str) -> str:
    normalized = value.strip().lower()
    if normalized in ENGLISH_ALIASES:
        return "en"
    raise SystemExit(
        f"[ERROR] {field_name}='{value}' no válido. Esta skill está configurada para inglés. Usa: en"
    )


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise SystemExit(f"[ERROR] Valor booleano inválido: {value}. Usa true/false")


def canonical_weekday(value: str) -> str:
    raw = value.strip().lower()
    if raw in WEEKDAY_ALIASES:
        raw = WEEKDAY_ALIASES[raw]
    if raw not in WEEKDAYS:
        raise SystemExit(
            f"[ERROR] Día inválido: {value}. Usa monday..sunday (o mon..sun)."
        )
    return raw


def normalize_weekdays(raw_list: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for item in raw_list:
        canonical = canonical_weekday(item)
        if canonical not in seen:
            seen.add(canonical)
            ordered.append(canonical)
    return ordered


def normalize_ratio(value: float, field_name: str) -> float:
    if value < 0 or value > 1:
        raise SystemExit(f"[ERROR] {field_name} debe estar entre 0 y 1. Valor: {value}")
    return round(float(value), 3)


def canonical_hashtag(token: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_]", "", token.strip().lstrip("#"))
    if not clean:
        return ""
    return f"#{clean.lower()}"


def suggest_hashtags(topic: str, tags: list[str], domain: str, min_count: int, max_count: int) -> list[str]:
    candidates: list[str] = []
    candidates.extend(tags)
    candidates.extend(re.findall(r"[A-Za-z0-9]+", topic))
    candidates.extend(re.findall(r"[A-Za-z0-9]+", domain))
    candidates.extend(["linkedin", "ai", "traveltech"])

    output: list[str] = []
    seen: set[str] = set()
    for token in candidates:
        tag = canonical_hashtag(token)
        if not tag or tag in seen:
            continue
        seen.add(tag)
        output.append(tag)
        if len(output) >= max_count:
            break

    if len(output) < min_count:
        raise SystemExit(
            f"[ERROR] No se pudieron generar suficientes hashtags (mínimo {min_count})."
        )

    return output[:max_count]


def normalize_hashtags(raw_hashtags: str, tags: list[str], topic: str, domain: str, min_count: int, max_count: int) -> list[str]:
    provided = [canonical_hashtag(item) for item in split_csv(raw_hashtags)]
    provided = [item for item in provided if item]

    deduped: list[str] = []
    seen: set[str] = set()
    for item in provided:
        if item not in seen:
            seen.add(item)
            deduped.append(item)

    if not deduped or len(deduped) < min_count:
        deduped = suggest_hashtags(topic=topic, tags=tags, domain=domain, min_count=min_count, max_count=max_count)

    return deduped[:max_count]


def default_settings() -> dict[str, Any]:
    return {
        "preferred_language": "en",
        "suggested_language": "en",
        "content_mix": {
            "shared_content_target_ratio": 0.65,
            "reflection_required_for_shared": True,
            "min_hashtags": 3,
            "max_hashtags": 8,
        },
        "calendar": {
            "objective_posts_per_week": 3,
            "planning_horizon_weeks": 4,
            "preferred_weekdays": ["monday", "wednesday", "friday"],
            "timezone": "UTC",
        },
    }


def default_profile() -> dict[str, Any]:
    ts = now_iso()
    return {
        "created_at": ts,
        "updated_at": ts,
        "settings": default_settings(),
        "interests": [],
        "publications": [],
        "feedback": [],
        "theme_goals": [],
        "calendar_entries": [],
        "learning": {
            "notes": [],
            "preferred_tones": [],
            "preferred_formats": [],
        },
    }


def default_memory() -> dict[str, Any]:
    ts = now_iso()
    return {
        "version": "2.1.0",
        "created_at": ts,
        "updated_at": ts,
        "profiles": {},
    }


def load_memory() -> dict[str, Any]:
    if not MEMORY_FILE.exists():
        memory = default_memory()
        save_memory(memory)
        return memory

    with MEMORY_FILE.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"[ERROR] JSON inválido en {MEMORY_FILE}: {exc}") from exc

    if not isinstance(data, dict):
        raise SystemExit(f"[ERROR] Formato inválido en {MEMORY_FILE}: se esperaba objeto JSON")

    data.setdefault("version", "2.1.0")
    data.setdefault("created_at", now_iso())
    data.setdefault("updated_at", now_iso())
    data.setdefault("profiles", {})
    return data


def save_memory(memory: dict[str, Any]) -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    memory["updated_at"] = now_iso()
    tmp_file = MEMORY_FILE.with_suffix(".json.tmp")
    with tmp_file.open("w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp_file, MEMORY_FILE)


def deep_merge_defaults(target: dict[str, Any], defaults: dict[str, Any]) -> None:
    for key, value in defaults.items():
        if key not in target:
            target[key] = value
            continue
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            deep_merge_defaults(target[key], value)


def ensure_profile(memory: dict[str, Any], profile: str) -> dict[str, Any]:
    profiles = memory.setdefault("profiles", {})
    if profile not in profiles:
        profiles[profile] = default_profile()

    profile_data = profiles[profile]
    if not isinstance(profile_data, dict):
        profiles[profile] = default_profile()
        profile_data = profiles[profile]

    deep_merge_defaults(profile_data, default_profile())

    # Enforce english-only language configuration
    settings = profile_data["settings"]
    settings["preferred_language"] = normalize_language(
        settings.get("preferred_language", "en"), "preferred_language"
    )
    settings["suggested_language"] = normalize_language(
        settings.get("suggested_language", "en"), "suggested_language"
    )

    content_mix = settings["content_mix"]
    content_mix["shared_content_target_ratio"] = normalize_ratio(
        float(content_mix.get("shared_content_target_ratio", 0.65)),
        "shared_content_target_ratio",
    )
    content_mix["reflection_required_for_shared"] = bool(
        content_mix.get("reflection_required_for_shared", True)
    )
    content_mix["min_hashtags"] = int(content_mix.get("min_hashtags", 3))
    content_mix["max_hashtags"] = int(content_mix.get("max_hashtags", 8))
    if content_mix["min_hashtags"] < 1:
        content_mix["min_hashtags"] = 1
    if content_mix["max_hashtags"] < content_mix["min_hashtags"]:
        content_mix["max_hashtags"] = content_mix["min_hashtags"]

    calendar = settings["calendar"]
    calendar["objective_posts_per_week"] = max(1, int(calendar.get("objective_posts_per_week", 3)))
    calendar["planning_horizon_weeks"] = max(1, int(calendar.get("planning_horizon_weeks", 4)))
    calendar["preferred_weekdays"] = normalize_weekdays(
        calendar.get("preferred_weekdays", ["monday", "wednesday", "friday"])
    )
    calendar["timezone"] = str(calendar.get("timezone", "UTC"))

    profile_data["updated_at"] = now_iso()
    return profile_data


def mk_id(prefix: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{stamp}_{uuid.uuid4().hex[:6]}"


def parse_date_iso(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f"[ERROR] Fecha inválida: {value}. Usa formato YYYY-MM-DD") from exc


def _engagement_value(item: dict[str, Any]) -> float:
    metrics = item.get("metrics", {})
    likes = float(metrics.get("likes", 0))
    comments = float(metrics.get("comments", 0))
    shares = float(metrics.get("shares", 0))
    saves = float(metrics.get("saves", 0))
    score = float(item.get("score", 0) or 0)
    return likes + (2 * comments) + (3 * shares) + (2 * saves) + (5 * score)


def cmd_init(args: argparse.Namespace) -> None:
    memory = load_memory()
    profile_data = ensure_profile(memory, args.profile)

    if args.preferred_language:
        profile_data["settings"]["preferred_language"] = normalize_language(
            args.preferred_language, "preferred_language"
        )
    if args.suggested_language:
        profile_data["settings"]["suggested_language"] = normalize_language(
            args.suggested_language, "suggested_language"
        )

    save_memory(memory)
    print(
        json.dumps(
            {
                "ok": True,
                "profile": args.profile,
                "memory_path": str(MEMORY_FILE),
                "language": {
                    "preferred": profile_data["settings"]["preferred_language"],
                    "suggested": profile_data["settings"]["suggested_language"],
                },
                "counts": {
                    "interests": len(profile_data.get("interests", [])),
                    "publications": len(profile_data.get("publications", [])),
                    "feedback": len(profile_data.get("feedback", [])),
                    "theme_goals": len(profile_data.get("theme_goals", [])),
                    "calendar_entries": len(profile_data.get("calendar_entries", [])),
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_set_config(args: argparse.Namespace) -> None:
    memory = load_memory()
    profile_data = ensure_profile(memory, args.profile)
    settings = profile_data["settings"]

    if args.preferred_language is not None:
        settings["preferred_language"] = normalize_language(
            args.preferred_language, "preferred_language"
        )
    if args.suggested_language is not None:
        settings["suggested_language"] = normalize_language(
            args.suggested_language, "suggested_language"
        )

    content_mix = settings["content_mix"]
    if args.shared_content_target_ratio is not None:
        content_mix["shared_content_target_ratio"] = normalize_ratio(
            args.shared_content_target_ratio, "shared_content_target_ratio"
        )
    if args.reflection_required_for_shared is not None:
        content_mix["reflection_required_for_shared"] = parse_bool(
            args.reflection_required_for_shared
        )
    if args.min_hashtags is not None:
        content_mix["min_hashtags"] = max(1, int(args.min_hashtags))
    if args.max_hashtags is not None:
        content_mix["max_hashtags"] = max(1, int(args.max_hashtags))
    if content_mix["max_hashtags"] < content_mix["min_hashtags"]:
        raise SystemExit(
            "[ERROR] max_hashtags no puede ser menor que min_hashtags"
        )

    calendar = settings["calendar"]
    if args.objective_posts_per_week is not None:
        calendar["objective_posts_per_week"] = max(1, int(args.objective_posts_per_week))
    if args.planning_horizon_weeks is not None:
        calendar["planning_horizon_weeks"] = max(1, int(args.planning_horizon_weeks))
    if args.preferred_weekdays:
        calendar["preferred_weekdays"] = normalize_weekdays(split_csv(args.preferred_weekdays))
    if args.timezone:
        calendar["timezone"] = args.timezone.strip()

    save_memory(memory)
    print(
        json.dumps(
            {
                "ok": True,
                "profile": args.profile,
                "memory_path": str(MEMORY_FILE),
                "settings": settings,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_show_config(args: argparse.Namespace) -> None:
    memory = load_memory()
    profile_data = ensure_profile(memory, args.profile)
    print(
        json.dumps(
            {
                "profile": args.profile,
                "memory_path": str(MEMORY_FILE),
                "settings": profile_data.get("settings", {}),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_add_interest(args: argparse.Namespace) -> None:
    memory = load_memory()
    profile_data = ensure_profile(memory, args.profile)
    interests = profile_data.setdefault("interests", [])

    domain_key = args.domain.strip().lower()
    topic_key = args.topic.strip().lower()

    existing = next(
        (
            item
            for item in interests
            if item.get("domain", "").strip().lower() == domain_key
            and item.get("topic", "").strip().lower() == topic_key
        ),
        None,
    )

    if existing:
        existing["mentions"] = int(existing.get("mentions", 1)) + 1
        if args.notes:
            notes = existing.setdefault("notes_history", [])
            notes.append({"note": args.notes.strip(), "at": now_iso()})
        existing["updated_at"] = now_iso()
        action = "updated"
        interest_id = existing.get("id")
    else:
        entry = {
            "id": mk_id("int"),
            "domain": args.domain.strip(),
            "topic": args.topic.strip(),
            "weight": float(args.weight),
            "mentions": 1,
            "notes": args.notes.strip() if args.notes else "",
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }
        interests.append(entry)
        action = "created"
        interest_id = entry["id"]

    save_memory(memory)
    print(
        json.dumps(
            {
                "ok": True,
                "action": action,
                "profile": args.profile,
                "interest_id": interest_id,
                "memory_path": str(MEMORY_FILE),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_add_theme_goal(args: argparse.Namespace) -> None:
    memory = load_memory()
    profile_data = ensure_profile(memory, args.profile)
    theme_goals = profile_data.setdefault("theme_goals", [])

    preferred_types = split_csv(args.preferred_content_types)
    if not preferred_types:
        preferred_types = ["news-share", "video-share", "insight"]

    valid_types = {"news-share", "video-share", "insight"}
    for content_type in preferred_types:
        if content_type not in valid_types:
            raise SystemExit(
                f"[ERROR] preferred_content_types incluye '{content_type}', no válido. "
                f"Permitidos: {sorted(valid_types)}"
            )

    preferred_weekdays = normalize_weekdays(split_csv(args.preferred_weekdays)) if args.preferred_weekdays else []

    key_domain = args.domain.strip().lower()
    key_theme = args.theme.strip().lower()
    existing = next(
        (
            item
            for item in theme_goals
            if item.get("domain", "").strip().lower() == key_domain
            and item.get("theme", "").strip().lower() == key_theme
        ),
        None,
    )

    if existing:
        existing["posts_per_month"] = int(args.posts_per_month)
        existing["priority"] = int(args.priority)
        existing["preferred_content_types"] = preferred_types
        if preferred_weekdays:
            existing["preferred_weekdays"] = preferred_weekdays
        if args.notes:
            existing["notes"] = args.notes.strip()
        existing["updated_at"] = now_iso()
        action = "updated"
        goal_id = existing["id"]
    else:
        entry = {
            "id": mk_id("goal"),
            "domain": args.domain.strip(),
            "theme": args.theme.strip(),
            "posts_per_month": int(args.posts_per_month),
            "priority": int(args.priority),
            "preferred_content_types": preferred_types,
            "preferred_weekdays": preferred_weekdays,
            "notes": args.notes.strip() if args.notes else "",
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }
        theme_goals.append(entry)
        action = "created"
        goal_id = entry["id"]

    save_memory(memory)
    print(
        json.dumps(
            {
                "ok": True,
                "action": action,
                "profile": args.profile,
                "goal_id": goal_id,
                "memory_path": str(MEMORY_FILE),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_add_publication(args: argparse.Namespace) -> None:
    memory = load_memory()
    profile_data = ensure_profile(memory, args.profile)
    publications = profile_data.setdefault("publications", [])

    settings = profile_data["settings"]
    content_mix = settings["content_mix"]

    language = normalize_language(
        args.language if args.language else settings.get("suggested_language", "en"),
        "language",
    )

    content_type = args.content_type
    is_shared = content_type in SHARED_CONTENT_TYPES

    shared_url = args.shared_url.strip() if args.shared_url else ""
    reflection = args.reflection.strip() if args.reflection else ""

    if is_shared and not shared_url:
        raise SystemExit(
            "[ERROR] Para content_type=news-share/video-share debes pasar --shared-url"
        )

    if is_shared and content_mix.get("reflection_required_for_shared", True) and not reflection:
        raise SystemExit(
            "[ERROR] Para publicaciones compartidas se requiere reflexión. Pasa --reflection"
        )

    tags = split_csv(args.tags)
    hashtags = normalize_hashtags(
        raw_hashtags=args.hashtags,
        tags=tags,
        topic=args.topic,
        domain=args.domain,
        min_count=int(content_mix.get("min_hashtags", 3)),
        max_count=int(content_mix.get("max_hashtags", 8)),
    )

    publication_id = mk_id("pub")
    entry = {
        "id": publication_id,
        "domain": args.domain.strip(),
        "topic": args.topic.strip(),
        "language": language,
        "content_type": content_type,
        "title": args.title.strip(),
        "hook": args.hook.strip(),
        "angle": args.angle.strip(),
        "draft": args.draft.strip(),
        "cta": args.cta.strip() if args.cta else "",
        "reflection": reflection,
        "shared_url": shared_url,
        "sources": split_csv(args.sources),
        "tags": tags,
        "hashtags": hashtags,
        "status": args.status,
        "calendar_entry_id": args.calendar_entry_id.strip() if args.calendar_entry_id else "",
        "scheduled_for": args.scheduled_for.strip() if args.scheduled_for else "",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "feedback_ids": [],
    }
    publications.append(entry)

    if entry["calendar_entry_id"]:
        for calendar_entry in profile_data.setdefault("calendar_entries", []):
            if calendar_entry.get("id") == entry["calendar_entry_id"]:
                calendar_entry["status"] = "published"
                calendar_entry["publication_id"] = publication_id
                calendar_entry["updated_at"] = now_iso()
                break

    save_memory(memory)
    print(
        json.dumps(
            {
                "ok": True,
                "profile": args.profile,
                "publication_id": publication_id,
                "memory_path": str(MEMORY_FILE),
                "language": language,
                "content_type": content_type,
                "hashtags": hashtags,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_add_feedback(args: argparse.Namespace) -> None:
    memory = load_memory()
    profile_data = ensure_profile(memory, args.profile)
    publications = profile_data.setdefault("publications", [])
    feedback = profile_data.setdefault("feedback", [])

    publication = next((p for p in publications if p.get("id") == args.publication_id), None)
    if not publication:
        raise SystemExit(
            f"[ERROR] publication_id no encontrado: {args.publication_id}. Usa summary para ver IDs válidos."
        )

    feedback_id = mk_id("fb")
    entry = {
        "id": feedback_id,
        "publication_id": args.publication_id,
        "score": int(args.score),
        "notes": args.notes.strip() if args.notes else "",
        "metrics": {
            "likes": int(args.likes),
            "comments": int(args.comments),
            "shares": int(args.shares),
            "saves": int(args.saves),
        },
        "published_url": args.published_url.strip() if args.published_url else "",
        "created_at": now_iso(),
    }
    feedback.append(entry)

    publication.setdefault("feedback_ids", []).append(feedback_id)
    if args.status:
        publication["status"] = args.status
    if args.published_url:
        publication["published_url"] = args.published_url.strip()
    publication["updated_at"] = now_iso()

    if args.preference_note:
        learning = profile_data.setdefault("learning", {})
        notes = learning.setdefault("notes", [])
        notes.append({"note": args.preference_note.strip(), "at": now_iso()})

    save_memory(memory)
    print(
        json.dumps(
            {
                "ok": True,
                "profile": args.profile,
                "feedback_id": feedback_id,
                "publication_id": args.publication_id,
                "memory_path": str(MEMORY_FILE),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def topic_performance(profile_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    interests = profile_data.get("interests", [])
    publications = profile_data.get("publications", [])
    feedback = profile_data.get("feedback", [])

    publication_by_id = {p.get("id"): p for p in publications}

    stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "topic": "",
            "domain": "",
            "interest_mentions": 0,
            "publications": 0,
            "shared_publications": 0,
            "feedback_count": 0,
            "engagement_score": 0.0,
            "blended_score": 0.0,
        }
    )

    for item in interests:
        key = item.get("topic", "").strip().lower()
        if not key:
            continue
        stat = stats[key]
        stat["topic"] = item.get("topic", "")
        stat["domain"] = item.get("domain", "")
        stat["interest_mentions"] += int(item.get("mentions", 1))

    for pub in publications:
        key = pub.get("topic", "").strip().lower()
        if not key:
            continue
        stat = stats[key]
        stat["topic"] = pub.get("topic", stat.get("topic", ""))
        stat["domain"] = pub.get("domain", stat.get("domain", ""))
        stat["publications"] += 1
        if pub.get("content_type") in SHARED_CONTENT_TYPES:
            stat["shared_publications"] += 1

    for fb in feedback:
        publication = publication_by_id.get(fb.get("publication_id"))
        if not publication:
            continue
        key = publication.get("topic", "").strip().lower()
        if not key:
            continue
        stat = stats[key]
        stat["feedback_count"] += 1
        stat["engagement_score"] += _engagement_value(fb)

    for stat in stats.values():
        stat["blended_score"] = (
            stat["interest_mentions"] * 1.0
            + stat["publications"] * 1.5
            + stat["feedback_count"] * 2.0
            + stat["engagement_score"] * 0.1
        )

    return stats


def build_slot_dates(start_date: date, weeks: int, objective_posts_per_week: int, preferred_weekdays: list[str]) -> list[date]:
    preferred = preferred_weekdays[:] if preferred_weekdays else ["monday", "wednesday", "friday"]
    while len(preferred) < objective_posts_per_week:
        for day_name in WEEKDAYS:
            if day_name not in preferred:
                preferred.append(day_name)
            if len(preferred) >= objective_posts_per_week:
                break

    selected = set(preferred[:objective_posts_per_week])
    total_slots = weeks * objective_posts_per_week

    slots: list[date] = []
    cursor = start_date
    end_date = start_date + timedelta(days=weeks * 7)

    while cursor < end_date and len(slots) < total_slots:
        if WEEKDAYS[cursor.weekday()] in selected:
            slots.append(cursor)
        cursor += timedelta(days=1)

    while len(slots) < total_slots:
        slots.append(cursor)
        cursor += timedelta(days=1)

    return slots


def choose_content_type(preferred_types: list[str], require_shared: bool, idx: int) -> str:
    if require_shared:
        for item in preferred_types:
            if item in SHARED_CONTENT_TYPES:
                return item
        return "news-share" if idx % 2 == 0 else "video-share"

    for item in preferred_types:
        if item == "insight":
            return item

    for item in preferred_types:
        if item not in SHARED_CONTENT_TYPES:
            return item

    return "insight"


def cmd_generate_calendar(args: argparse.Namespace) -> None:
    memory = load_memory()
    profile_data = ensure_profile(memory, args.profile)

    settings = profile_data["settings"]
    calendar_cfg = settings["calendar"]
    mix_cfg = settings["content_mix"]

    weeks = int(args.weeks) if args.weeks else int(calendar_cfg.get("planning_horizon_weeks", 4))
    objective_posts_per_week = int(args.objective_posts_per_week) if args.objective_posts_per_week else int(
        calendar_cfg.get("objective_posts_per_week", 3)
    )

    if args.start_date:
        start_date = parse_date_iso(args.start_date)
    else:
        start_date = date.today()

    preferred_weekdays = (
        normalize_weekdays(split_csv(args.preferred_weekdays))
        if args.preferred_weekdays
        else normalize_weekdays(calendar_cfg.get("preferred_weekdays", ["monday", "wednesday", "friday"]))
    )

    slots = build_slot_dates(
        start_date=start_date,
        weeks=max(1, weeks),
        objective_posts_per_week=max(1, objective_posts_per_week),
        preferred_weekdays=preferred_weekdays,
    )

    performance = topic_performance(profile_data)
    goals = profile_data.get("theme_goals", [])

    if not goals:
        for key, stat in sorted(
            performance.items(), key=lambda kv: kv[1].get("blended_score", 0), reverse=True
        )[:5]:
            goals.append(
                {
                    "id": mk_id("goal"),
                    "domain": stat.get("domain") or "general",
                    "theme": stat.get("topic") or key,
                    "posts_per_month": 4,
                    "priority": 3,
                    "preferred_content_types": ["news-share", "video-share", "insight"],
                    "preferred_weekdays": [],
                    "created_at": now_iso(),
                    "updated_at": now_iso(),
                }
            )

    if not goals:
        raise SystemExit(
            "[ERROR] No hay theme_goals ni topics históricos. Añade al menos un interés o un theme-goal primero."
        )

    theme_states: list[dict[str, Any]] = []
    for goal in goals:
        theme_key = goal.get("theme", "").strip().lower()
        perf = performance.get(theme_key, {})
        posts_per_month = max(1, int(goal.get("posts_per_month", 4)))
        priority = max(1, int(goal.get("priority", 3)))

        target_posts = max(1, round(posts_per_month * (len(slots) / max(1, objective_posts_per_week * 4))))
        score = (
            priority * 10
            + float(perf.get("interest_mentions", 0)) * 2.0
            + float(perf.get("feedback_count", 0)) * 3.0
            + float(perf.get("engagement_score", 0)) * 0.05
        )

        preferred_types = goal.get("preferred_content_types", ["news-share", "video-share", "insight"])
        if not preferred_types:
            preferred_types = ["news-share", "video-share", "insight"]

        theme_states.append(
            {
                "goal_id": goal.get("id", ""),
                "domain": goal.get("domain", "general"),
                "theme": goal.get("theme", "general"),
                "preferred_content_types": preferred_types,
                "target_posts": target_posts,
                "remaining": target_posts,
                "planned": 0,
                "score": score,
            }
        )

    if not theme_states:
        raise SystemExit("[ERROR] No se pudieron construir themes para el calendario")

    total_slots = len(slots)
    shared_ratio = normalize_ratio(
        float(args.shared_content_target_ratio)
        if args.shared_content_target_ratio is not None
        else float(mix_cfg.get("shared_content_target_ratio", 0.65)),
        "shared_content_target_ratio",
    )
    shared_target = round(total_slots * shared_ratio)

    if args.replace_planned:
        profile_data["calendar_entries"] = [
            item for item in profile_data.get("calendar_entries", []) if item.get("status") != "planned"
        ]

    shared_assigned = 0
    last_theme = ""
    new_entries: list[dict[str, Any]] = []

    for idx, slot in enumerate(slots):
        ranked = sorted(
            theme_states,
            key=lambda s: (
                s["remaining"] > 0,
                s["remaining"],
                s["score"] - (s["planned"] * 0.35),
            ),
            reverse=True,
        )

        chosen = ranked[0]
        if len(ranked) > 1 and chosen["theme"].strip().lower() == last_theme:
            alt = ranked[1]
            if alt["remaining"] > 0 or alt["score"] >= chosen["score"] - 1:
                chosen = alt

        should_assign_shared_now = shared_assigned < round(((idx + 1) * shared_target) / max(1, total_slots))
        content_type = choose_content_type(
            preferred_types=chosen.get("preferred_content_types", []),
            require_shared=should_assign_shared_now,
            idx=idx,
        )

        if content_type in SHARED_CONTENT_TYPES:
            shared_assigned += 1

        chosen["planned"] += 1
        if chosen["remaining"] > 0:
            chosen["remaining"] -= 1

        hashtags_hint = suggest_hashtags(
            topic=chosen["theme"],
            tags=[chosen["domain"]],
            domain=chosen["domain"],
            min_count=int(mix_cfg.get("min_hashtags", 3)),
            max_count=int(mix_cfg.get("max_hashtags", 8)),
        )

        entry_id = mk_id("cal")
        entry = {
            "id": entry_id,
            "goal_id": chosen.get("goal_id", ""),
            "scheduled_date": slot.isoformat(),
            "weekday": WEEKDAYS[slot.weekday()],
            "domain": chosen["domain"],
            "theme": chosen["theme"],
            "content_type": content_type,
            "language": settings.get("suggested_language", "en"),
            "status": "planned",
            "source_required": content_type in SHARED_CONTENT_TYPES,
            "reflection_required": bool(mix_cfg.get("reflection_required_for_shared", True))
            if content_type in SHARED_CONTENT_TYPES
            else False,
            "hashtags_hint": hashtags_hint,
            "notes": "Share external news/video + add your reflection" if content_type in SHARED_CONTENT_TYPES else "Original insight post",
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }
        new_entries.append(entry)
        last_theme = chosen["theme"].strip().lower()

    profile_data.setdefault("calendar_entries", []).extend(new_entries)
    save_memory(memory)

    print(
        json.dumps(
            {
                "ok": True,
                "profile": args.profile,
                "memory_path": str(MEMORY_FILE),
                "generated_entries": len(new_entries),
                "shared_target_ratio": shared_ratio,
                "shared_entries": len(
                    [item for item in new_entries if item.get("content_type") in SHARED_CONTENT_TYPES]
                ),
                "entries_preview": new_entries[:10],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_calendar(args: argparse.Namespace) -> None:
    memory = load_memory()
    profile_data = ensure_profile(memory, args.profile)
    entries = profile_data.get("calendar_entries", [])

    today = date.today()
    until = today + timedelta(days=max(1, int(args.days)))

    filtered = []
    for item in entries:
        scheduled = item.get("scheduled_date", "")
        try:
            scheduled_date = date.fromisoformat(scheduled)
        except ValueError:
            continue

        if scheduled_date < today or scheduled_date > until:
            continue

        if not args.include_non_planned and item.get("status") != "planned":
            continue

        filtered.append(item)

    filtered.sort(key=lambda x: x.get("scheduled_date", ""))
    filtered = filtered[: max(1, int(args.limit))]

    print(
        json.dumps(
            {
                "profile": args.profile,
                "memory_path": str(MEMORY_FILE),
                "window": {
                    "from": today.isoformat(),
                    "to": until.isoformat(),
                },
                "count": len(filtered),
                "entries": filtered,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_summary(args: argparse.Namespace) -> None:
    memory = load_memory()
    profile_data = ensure_profile(memory, args.profile)

    interests = profile_data.get("interests", [])
    publications = profile_data.get("publications", [])
    feedback = profile_data.get("feedback", [])
    theme_goals = profile_data.get("theme_goals", [])
    calendar_entries = profile_data.get("calendar_entries", [])

    stats = topic_performance(profile_data)
    top_topics = sorted(stats.values(), key=lambda x: x.get("blended_score", 0), reverse=True)[: args.top]

    recent_publications = sorted(
        publications,
        key=lambda x: x.get("created_at", ""),
        reverse=True,
    )[:3]

    recent_feedback = sorted(
        feedback,
        key=lambda x: x.get("created_at", ""),
        reverse=True,
    )[:3]

    shared_publications = [p for p in publications if p.get("content_type") in SHARED_CONTENT_TYPES]
    with_hashtags = [p for p in publications if p.get("hashtags")]

    planned_entries = [entry for entry in calendar_entries if entry.get("status") == "planned"]
    next_calendar = sorted(planned_entries, key=lambda x: x.get("scheduled_date", ""))[:5]

    output = {
        "profile": args.profile,
        "memory_path": str(MEMORY_FILE),
        "settings": profile_data.get("settings", {}),
        "counts": {
            "interests": len(interests),
            "publications": len(publications),
            "feedback": len(feedback),
            "theme_goals": len(theme_goals),
            "calendar_entries": len(calendar_entries),
            "calendar_planned": len(planned_entries),
        },
        "content_mix_tracking": {
            "shared_publications": len(shared_publications),
            "shared_ratio": round(len(shared_publications) / len(publications), 3) if publications else 0,
            "hashtag_coverage": round(len(with_hashtags) / len(publications), 3) if publications else 0,
        },
        "top_topics": top_topics,
        "next_calendar_entries": next_calendar,
        "recent_publications": [
            {
                "id": p.get("id"),
                "domain": p.get("domain"),
                "topic": p.get("topic"),
                "title": p.get("title"),
                "content_type": p.get("content_type", "insight"),
                "language": p.get("language", "en"),
                "hashtags": p.get("hashtags", []),
                "status": p.get("status"),
                "created_at": p.get("created_at"),
            }
            for p in recent_publications
        ],
        "recent_feedback": recent_feedback,
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Memoria local para la skill de LinkedIn: configuración, intereses, propuestas, feedback y calendario por temas."
        )
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Inicializa memoria y perfil")
    p_init.add_argument("--profile", default="default", help="ID de perfil (ej: javier-linkedin)")
    p_init.add_argument("--preferred-language", default=None, help="Idioma preferido (solo en)")
    p_init.add_argument("--suggested-language", default=None, help="Idioma sugerido para posts (solo en)")
    p_init.set_defaults(func=cmd_init)

    p_set = sub.add_parser("set-config", help="Actualiza configuración del perfil")
    p_set.add_argument("--profile", default="default")
    p_set.add_argument("--preferred-language", default=None, help="Idioma preferido (solo en)")
    p_set.add_argument("--suggested-language", default=None, help="Idioma sugerido para posts (solo en)")
    p_set.add_argument("--shared-content-target-ratio", type=float, default=None, help="Ratio objetivo de posts news/video compartidos (0-1)")
    p_set.add_argument("--reflection-required-for-shared", default=None, help="true/false. Si true, exige reflexión en posts compartidos")
    p_set.add_argument("--min-hashtags", type=int, default=None)
    p_set.add_argument("--max-hashtags", type=int, default=None)
    p_set.add_argument("--objective-posts-per-week", type=int, default=None)
    p_set.add_argument("--planning-horizon-weeks", type=int, default=None)
    p_set.add_argument("--preferred-weekdays", default=None, help="CSV: monday,wednesday,friday")
    p_set.add_argument("--timezone", default=None)
    p_set.set_defaults(func=cmd_set_config)

    p_show = sub.add_parser("show-config", help="Muestra configuración actual del perfil")
    p_show.add_argument("--profile", default="default")
    p_show.set_defaults(func=cmd_show_config)

    p_interest = sub.add_parser("add-interest", help="Guarda o actualiza tema de interés")
    p_interest.add_argument("--profile", default="default")
    p_interest.add_argument("--domain", required=True, help="Ámbito (ej: travel-tech)")
    p_interest.add_argument("--topic", required=True, help="Tema de interés")
    p_interest.add_argument("--weight", default=1.0, type=float)
    p_interest.add_argument("--notes", default="")
    p_interest.set_defaults(func=cmd_add_interest)

    p_goal = sub.add_parser("add-theme-goal", help="Define objetivo de calendario por tema")
    p_goal.add_argument("--profile", default="default")
    p_goal.add_argument("--domain", required=True)
    p_goal.add_argument("--theme", required=True)
    p_goal.add_argument("--posts-per-month", type=int, default=4)
    p_goal.add_argument("--priority", type=int, default=3, help="1-5")
    p_goal.add_argument(
        "--preferred-content-types",
        default="news-share,video-share,insight",
        help="CSV con tipos permitidos: news-share,video-share,insight",
    )
    p_goal.add_argument("--preferred-weekdays", default="", help="CSV opcional")
    p_goal.add_argument("--notes", default="")
    p_goal.set_defaults(func=cmd_add_theme_goal)

    p_cal = sub.add_parser("generate-calendar", help="Genera calendario objetivo de publicaciones por tema")
    p_cal.add_argument("--profile", default="default")
    p_cal.add_argument("--weeks", type=int, default=None)
    p_cal.add_argument("--objective-posts-per-week", type=int, default=None)
    p_cal.add_argument("--preferred-weekdays", default="", help="CSV opcional")
    p_cal.add_argument("--start-date", default="", help="YYYY-MM-DD")
    p_cal.add_argument("--shared-content-target-ratio", type=float, default=None)
    p_cal.add_argument(
        "--replace-planned",
        action="store_true",
        help="Reemplaza entradas planned actuales antes de generar",
    )
    p_cal.set_defaults(func=cmd_generate_calendar)

    p_calendar = sub.add_parser("calendar", help="Lista calendario próximo")
    p_calendar.add_argument("--profile", default="default")
    p_calendar.add_argument("--days", type=int, default=45)
    p_calendar.add_argument("--limit", type=int, default=50)
    p_calendar.add_argument(
        "--include-non-planned",
        action="store_true",
        help="Incluye también entradas ya publicadas/descartadas",
    )
    p_calendar.set_defaults(func=cmd_calendar)

    p_pub = sub.add_parser("add-publication", help="Guarda propuesta o publicación")
    p_pub.add_argument("--profile", default="default")
    p_pub.add_argument("--domain", required=True)
    p_pub.add_argument("--topic", required=True)
    p_pub.add_argument("--title", required=True)
    p_pub.add_argument("--hook", required=True)
    p_pub.add_argument("--angle", required=True)
    p_pub.add_argument("--draft", required=True)
    p_pub.add_argument("--cta", default="")
    p_pub.add_argument(
        "--content-type",
        default="insight",
        choices=["insight", "news-share", "video-share"],
        help="Tipo de publicación. news/video requiere shared-url y reflexión",
    )
    p_pub.add_argument("--shared-url", default="", help="URL de noticia/video compartido")
    p_pub.add_argument("--reflection", default="", help="Reflexión personal sobre la noticia/video")
    p_pub.add_argument("--sources", default="", help="URLs separadas por coma")
    p_pub.add_argument("--tags", default="", help="Tags separadas por coma")
    p_pub.add_argument("--hashtags", default="", help="Hashtags CSV. Si faltan, se autogeneran")
    p_pub.add_argument("--language", default="", help="Idioma del post (solo en)")
    p_pub.add_argument("--calendar-entry-id", default="", help="ID de calendario (si viene de planificación)")
    p_pub.add_argument("--scheduled-for", default="", help="Fecha planificada YYYY-MM-DD")
    p_pub.add_argument(
        "--status",
        default="proposed",
        choices=["proposed", "selected", "published", "discarded"],
    )
    p_pub.set_defaults(func=cmd_add_publication)

    p_fb = sub.add_parser("add-feedback", help="Guarda feedback de una publicación")
    p_fb.add_argument("--profile", default="default")
    p_fb.add_argument("--publication-id", required=True)
    p_fb.add_argument("--score", type=int, default=0, help="Puntuación cualitativa 0-5")
    p_fb.add_argument("--notes", default="")
    p_fb.add_argument("--likes", type=int, default=0)
    p_fb.add_argument("--comments", type=int, default=0)
    p_fb.add_argument("--shares", type=int, default=0)
    p_fb.add_argument("--saves", type=int, default=0)
    p_fb.add_argument("--published-url", default="")
    p_fb.add_argument(
        "--status",
        default="",
        choices=["", "selected", "published", "discarded"],
    )
    p_fb.add_argument(
        "--preference-note",
        default="",
        help="Aprendizaje cualitativo del usuario (tono, formato, CTA, etc.)",
    )
    p_fb.set_defaults(func=cmd_add_feedback)

    p_summary = sub.add_parser("summary", help="Resumen para preparar siguientes publicaciones")
    p_summary.add_argument("--profile", default="default")
    p_summary.add_argument("--top", type=int, default=5)
    p_summary.set_defaults(func=cmd_summary)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
