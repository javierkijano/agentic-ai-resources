# -*- coding: utf-8 -*-
"""Loads defaults + user overrides + policies + modes + coaching banks."""
import copy
import glob
import os
from typing import Dict, List, Tuple

import yaml

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULTS_PATH = os.path.join(SKILL_DIR, "config", "defaults.yaml")
POLICIES_DIR = os.path.join(SKILL_DIR, "config", "policies")
MODES_DIR = os.path.join(SKILL_DIR, "config", "modes")
COACHING_DIR = os.path.join(SKILL_DIR, "config", "coaching")


def _deep_merge(base: dict, overlay: dict) -> dict:
    if not isinstance(base, dict) or not isinstance(overlay, dict):
        return copy.deepcopy(overlay) if overlay is not None else copy.deepcopy(base)
    out = copy.deepcopy(base)
    for k, v in overlay.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def _set_dotted(d: dict, dotted: str, value) -> None:
    parts = dotted.split(".")
    cur = d
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def load_yaml(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def load_defaults() -> dict:
    return load_yaml(DEFAULTS_PATH)


def load_user_config(path: str) -> dict:
    return load_yaml(path) if path and os.path.exists(path) else {}


def load_policies() -> List[dict]:
    files = sorted(glob.glob(os.path.join(POLICIES_DIR, "*.yaml")))
    policies = []
    for f in files:
        p = load_yaml(f)
        if not p:
            continue
        p.setdefault("_file", os.path.basename(f))
        p.setdefault("enabled", True)
        p.setdefault("priority", 100)
        policies.append(p)
    policies.sort(key=lambda x: x.get("priority", 100))
    return policies


def load_mode(mode_name: str) -> dict:
    path = os.path.join(MODES_DIR, f"{mode_name}.yaml")
    return load_yaml(path)


def load_coaching_banks(themes: List[str]) -> Dict[str, dict]:
    banks = {}
    for theme in themes or []:
        path = os.path.join(COACHING_DIR, f"{theme}.yaml")
        data = load_yaml(path)
        if data:
            banks[theme] = data
    return banks


def build_effective_config(user_config_path: str = None) -> Tuple[dict, dict]:
    """Returns (effective_config, mode_info).

    mode_info = {
      'name': <mode>,
      'policy_filters': {...},  # from mode file
    }
    """
    defaults = load_defaults()
    user = load_user_config(user_config_path) if user_config_path else {}
    cfg = _deep_merge(defaults, user)

    mode_name = cfg.get("preferences", {}).get("primary_mode", "operator")
    mode = load_mode(mode_name) or {}
    overrides = mode.get("overrides", {}) or {}
    # mode overrides use dotted keys
    for dotted, value in overrides.items():
        _set_dotted(cfg, dotted, value)

    mode_info = {
        "name": mode_name,
        "policy_filters": mode.get("policy_filters", {}) or {},
    }
    return cfg, mode_info


def filter_policies_by_mode(policies: List[dict], mode_info: dict) -> List[dict]:
    pf = mode_info.get("policy_filters", {}) or {}
    disabled = set(pf.get("disable", []) or [])
    only_critical = bool(pf.get("enable_only_critical", False))
    out = []
    for p in policies:
        if not p.get("enabled", True):
            continue
        if p.get("id") in disabled:
            continue
        if only_critical and p.get("urgency") != "critical":
            continue
        out.append(p)
    return out
