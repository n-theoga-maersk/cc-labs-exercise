# 0007. Split the backend into an `app/` package with one router per area

- **Status:** Accepted
- **Date:** 2026-10-05
- **Source:** PR #1 in the n-theoga-maersk fork (`refactor/modular-backend-and-docs`)

## Context
All of the backend lived in a single ~300-line `server/main.py`: Pydantic models, filter helpers, CORS setup and 14 routes across six unrelated areas, with data loading in `mock_data.py`. The client already calls endpoints that don't exist yet (`/api/tasks`, `/api/purchase-orders`), so the file was about to grow. Two constraints applied:
- `uv run python main.py` (README, `scripts/start.sh`, `/start` command) must keep working.
- `tests/backend/conftest.py` imports `app` from `main`.

## Decision
```
server/main.py            entry point only: re-exports app.main.app, runs uvicorn
server/app/main.py        FastAPI app, CORS, root route, include_router loop
server/app/data.py        data loading (git mv from mock_data.py)
server/app/models.py      all Pydantic models
server/app/filters.py     apply_filters, filter_by_month, quarter_for, QUARTER_MAP
server/app/routers/*.py   one APIRouter per area, each owning its URL prefix and OpenAPI tag
```
Modules import absolutely from `server/` (`from app.data import orders`).

The refactor was strictly **behaviour-preserving**. We checked this by snapshotting 2,143 responses (every endpoint, plus every combination of warehouse, category, status and month filters, including invalid values and 404s) before and after. The only intended differences were OpenAPI tags and a UTF-8 decoding fix (see ADR-0002).

## Consequences
- A new area means a new router file plus one entry in the `include_router` loop. Shared filtering stays in one place.
- `/docs` groups endpoints by tag.
- Models live in one module rather than next to their routes. That's simple at this size, but could become a `models/` package if it grows.
- Known bugs that predate the refactor were deliberately **not** fixed, because the PR was kept behaviour-neutral. These are the substring month matching, unknown quarters returning unfiltered data, a dashboard backlog count that ignores filters, and an unrounded `total_orders_value`. They're listed in PR #1 as follow-ups.
- The snapshot technique is the recommended check for future refactors, because the existing tests assert structure rather than exact values.
