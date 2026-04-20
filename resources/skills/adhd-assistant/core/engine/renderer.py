# -*- coding: utf-8 -*-
"""Jinja2 renderer for policy message templates."""
import jinja2

_env = jinja2.Environment(
    undefined=jinja2.ChainableUndefined,
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
)


def render(template_str: str, ctx: dict) -> str:
    if not template_str:
        return ""
    tmpl = _env.from_string(template_str)
    return tmpl.render(**ctx).strip()
