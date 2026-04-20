# -*- coding: utf-8 -*-
"""FastAPI app for the ideas-con-hijos skill.

Run from the skill directory:
  python3 -m webapp.app
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

APP_DIR = Path(__file__).resolve().parent
SKILL_DIR = APP_DIR.parent
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))


def normalize_root_path(value: str | None) -> str:
    root = (value or "").strip()
    if not root or root == "/":
        return ""
    if not root.startswith("/"):
        root = f"/{root}"
    return root.rstrip("/")


APP_BASE_PATH = normalize_root_path(
    os.environ.get("KIDS_WEBAPP_ROOT_PATH") or os.environ.get("WEBAPP_ROOT_PATH", "")
)

from catalog import ActivityCatalog, CatalogPaths  # noqa: E402


catalog = ActivityCatalog(CatalogPaths.from_skill_dir(SKILL_DIR))

templates = Jinja2Templates(directory=str(APP_DIR / "templates"))

app = FastAPI(
    title="Chispas · ideas con hijos",
    description="Catálogo práctico de actividades familiares con procedencia explícita.",
    version="0.1.0",
)
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")


def request_base_path(request: Request) -> str:
    return normalize_root_path(request.scope.get("root_path") or APP_BASE_PATH)


@app.get("/")
def dashboard(request: Request):
    payload = catalog.build_dashboard()
    context = {
        "request": request,
        "bootstrap": payload,
        "app_base_path": request_base_path(request),
    }
    try:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context=context,
        )
    except TypeError:
        return templates.TemplateResponse("index.html", context)


@app.get("/api/health")
def api_health():
    summary = catalog.stats()
    return {
        "status": "ok",
        "activities": summary["total"],
        "featured": summary["featured"],
        "catalog_path": str(catalog.paths.activities_path),
    }


@app.get("/api/summary")
def api_summary():
    return catalog.stats()


@app.get("/api/facets")
def api_facets():
    return catalog.facets()


@app.get("/api/activities")
def api_activities(
    query: str = Query(default=""),
    activity_type: str | None = Query(default=None),
    context: str | None = Query(default=None),
    origin: str | None = Query(default=None),
    delivery_mode: str | None = Query(default=None),
    age: int | None = Query(default=None, ge=0),
    max_duration: int | None = Query(default=None, ge=1),
    featured_only: bool = Query(default=False),
    limit: int | None = Query(default=50, ge=1, le=200),
):
    results = catalog.search(
        query=query,
        activity_type=activity_type,
        context=context,
        origin=origin,
        delivery_mode=delivery_mode,
        age=age,
        max_duration=max_duration,
        featured_only=featured_only,
        limit=limit,
    )
    return {
        "count": len(results),
        "items": results,
    }


@app.get("/api/activities/{slug}")
def api_activity(slug: str):
    item = catalog.get(slug)
    if not item:
        raise HTTPException(status_code=404, detail=f"activity not found: {slug}")
    return item


@app.get("/api/dashboard")
def api_dashboard():
    return catalog.build_dashboard()


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": str(exc),
        },
    )


if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("KIDS_WEBAPP_HOST", "127.0.0.1")
    port = int(os.environ.get("KIDS_WEBAPP_PORT", "8766"))
    reload = os.environ.get("KIDS_WEBAPP_RELOAD", "0") in {"1", "true", "True"}

    uvicorn.run(app, host=host, port=port, reload=reload)
