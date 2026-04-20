#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Canonical skill-local tick launcher.

Cron jobs call this module directly from the skill tree; no external wrapper lives in ~/.hermes/scripts."""

from __future__ import annotations

import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from engine.tick import main

__all__ = ["main"]


if __name__ == "__main__":
    raise SystemExit(main())
