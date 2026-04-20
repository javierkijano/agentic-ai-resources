# -*- coding: utf-8 -*-
"""Data access and search helpers for the ideas-con-hijos skill."""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class CatalogPaths:
    skill_dir: Path
    activities_path: Path

    @classmethod
    def from_skill_dir(cls, skill_dir: Path) -> "CatalogPaths":
        skill_dir = skill_dir.resolve()
        return cls(
            skill_dir=skill_dir,
            activities_path=skill_dir / "data" / "activities.json",
        )


def _normalize(text: Any) -> str:
    raw = unicodedata.normalize("NFKD", str(text or ""))
    ascii_text = raw.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", ascii_text.lower()).strip()


def _tokens(text: Any) -> List[str]:
    return [token for token in _normalize(text).split() if len(token) >= 2]


def _provenance_label(origin_type: str) -> str:
    labels = {
        "internal_original": "Original",
        "adapted_from_source": "Adaptada",
        "external_reference": "Fuente externa",
    }
    return labels.get(origin_type, origin_type)


def _delivery_label(delivery_mode: str) -> str:
    labels = {
        "full_guide": "Guía completa",
        "hybrid": "Guía resumida + fuente",
        "external_link": "Explicación externa",
    }
    return labels.get(delivery_mode, delivery_mode)


class ActivityCatalog:
    def __init__(self, paths: CatalogPaths):
        self.paths = paths

    def load(self) -> List[Dict[str, Any]]:
        with self.paths.activities_path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        if not isinstance(raw, list):
            raise ValueError("activities.json must contain a list")
        activities = [self._decorate(dict(item)) for item in raw]
        return sorted(
            activities,
            key=lambda item: (-int(item.get("curation_rank", 999)), item.get("title", "")),
        )

    def _decorate(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        origin_type = str(activity.get("origin_type", "internal_original"))
        delivery_mode = str(activity.get("delivery_mode", "full_guide"))
        ages = activity.get("ages") or {}
        duration = activity.get("duration") or {}
        activity["provenance_label"] = _provenance_label(origin_type)
        activity["delivery_label"] = _delivery_label(delivery_mode)
        activity["age_label"] = ages.get("label") or f"{ages.get('min', '?')}+"
        activity["duration_label"] = duration.get("label") or f"{duration.get('min', '?')} min"
        activity["search_blob"] = " ".join(
            [
                activity.get("title", ""),
                activity.get("summary", ""),
                " ".join(activity.get("materials", [])),
                " ".join(activity.get("activity_types", [])),
                " ".join(activity.get("contexts", [])),
                " ".join(activity.get("what_develops", [])),
                " ".join(activity.get("search_tags", [])),
                str((activity.get("source") or {}).get("publisher", "")),
                str((activity.get("source") or {}).get("title", "")),
            ]
        )
        return activity

    def stats(self, activities: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
        items = activities if activities is not None else self.load()
        origin_counter = Counter(item.get("origin_type", "unknown") for item in items)
        type_counter = Counter(
            activity_type
            for item in items
            for activity_type in item.get("activity_types", [])
        )
        context_counter = Counter(
            context
            for item in items
            for context in item.get("contexts", [])
        )
        return {
            "total": len(items),
            "featured": sum(1 for item in items if item.get("featured")),
            "internal_original": origin_counter.get("internal_original", 0),
            "adapted_from_source": origin_counter.get("adapted_from_source", 0),
            "external_reference": origin_counter.get("external_reference", 0),
            "top_types": [
                {"value": key, "count": count}
                for key, count in type_counter.most_common(6)
            ],
            "top_contexts": [
                {"value": key, "count": count}
                for key, count in context_counter.most_common(6)
            ],
        }

    def facets(self, activities: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
        items = activities if activities is not None else self.load()

        def _sorted_counts(values: List[str]) -> List[Dict[str, Any]]:
            counts = Counter(values)
            return [
                {"value": key, "count": counts[key]}
                for key in sorted(counts)
            ]

        types = _sorted_counts(
            [value for item in items for value in item.get("activity_types", [])]
        )
        contexts = _sorted_counts(
            [value for item in items for value in item.get("contexts", [])]
        )
        origins = _sorted_counts([item.get("origin_type", "") for item in items])
        deliveries = _sorted_counts([item.get("delivery_mode", "") for item in items])

        age_buckets = []
        for age in [3, 4, 5, 6, 7, 8, 9]:
            count = sum(
                1
                for item in items
                if int((item.get("ages") or {}).get("min", 0)) <= age
                <= int((item.get("ages") or {}).get("max", 99))
            )
            age_buckets.append({"value": age, "count": count})

        duration_buckets = []
        for limit in [10, 15, 20, 30, 45]:
            count = sum(
                1
                for item in items
                if int((item.get("duration") or {}).get("max", 999)) <= limit
            )
            duration_buckets.append({"value": limit, "count": count})

        return {
            "types": types,
            "contexts": contexts,
            "origins": origins,
            "deliveries": deliveries,
            "ages": age_buckets,
            "durations": duration_buckets,
        }

    def get(self, slug: str) -> Dict[str, Any] | None:
        for item in self.load():
            if item.get("slug") == slug:
                return item
        return None

    def search(
        self,
        query: str = "",
        *,
        activity_type: str | None = None,
        context: str | None = None,
        origin: str | None = None,
        delivery_mode: str | None = None,
        age: int | None = None,
        max_duration: int | None = None,
        featured_only: bool = False,
        limit: int | None = None,
    ) -> List[Dict[str, Any]]:
        items = self.load()
        query_tokens = _tokens(query)
        activity_type = activity_type or None
        context = context or None
        origin = origin or None
        delivery_mode = delivery_mode or None

        ranked: List[Dict[str, Any]] = []
        for item in items:
            if featured_only and not item.get("featured"):
                continue
            if activity_type and activity_type not in item.get("activity_types", []):
                continue
            if context and context not in item.get("contexts", []):
                continue
            if origin and origin != item.get("origin_type"):
                continue
            if delivery_mode and delivery_mode != item.get("delivery_mode"):
                continue

            ages = item.get("ages") or {}
            if age is not None:
                if not (int(ages.get("min", 0)) <= age <= int(ages.get("max", 99))):
                    continue

            duration = item.get("duration") or {}
            if max_duration is not None and int(duration.get("max", 999)) > max_duration:
                continue

            score = int(item.get("curation_rank", 0))
            title_norm = _normalize(item.get("title", ""))
            summary_norm = _normalize(item.get("summary", ""))
            search_blob_norm = _normalize(item.get("search_blob", ""))
            materials_norm = _normalize(" ".join(item.get("materials", [])))
            type_norm = _normalize(" ".join(item.get("activity_types", [])))
            contexts_norm = _normalize(" ".join(item.get("contexts", [])))

            if query_tokens:
                for token in query_tokens:
                    if token in title_norm:
                        score += 12
                    if token in materials_norm:
                        score += 10
                    if token in type_norm or token in contexts_norm:
                        score += 8
                    if token in summary_norm:
                        score += 5
                    if token in search_blob_norm:
                        score += 2
                if score == int(item.get("curation_rank", 0)):
                    continue

            item_copy = dict(item)
            item_copy["score"] = score
            ranked.append(item_copy)

        ranked.sort(
            key=lambda item: (
                -int(item.get("score", 0)),
                int((item.get("duration") or {}).get("min", 999)),
                item.get("title", ""),
            )
        )
        if limit is not None:
            return ranked[:limit]
        return ranked

    def build_dashboard(self) -> Dict[str, Any]:
        activities = self.load()
        return {
            "summary": self.stats(activities),
            "facets": self.facets(activities),
            "featured": [item for item in activities if item.get("featured")][:4],
            "activities": activities,
        }
