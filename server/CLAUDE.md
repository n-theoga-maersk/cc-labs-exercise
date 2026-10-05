# CLAUDE.md - Server

Guidance for the FastAPI backend. Data rules are in `.claude/rules/data.md` and test rules in `.claude/rules/testing.md`.

## Running
Run and test commands are in the root `CLAUDE.md`. There's no hot reload, so restart after changes. The `tool.uv.dev-dependencies` deprecation warning from `uv sync` is harmless.

## Layout
```
server/
├── main.py              # entry point only: imports app.main.app and runs uvicorn
└── app/
    ├── main.py          # FastAPI app, CORS, root route, include_router for each router
    ├── data.py          # loads data/*.json once at import (see rules/data.md)
    ├── models.py        # all Pydantic models
    ├── filters.py       # apply_filters, filter_by_month, quarter_for, QUARTER_MAP
    └── routers/         # one APIRouter per area, each owning its URL prefix and OpenAPI tag
        ├── inventory.py   /api/inventory
        ├── orders.py      /api/orders
        ├── planning.py    /api/demand, /api/backlog
        ├── purchase_orders.py  /api/purchase-orders (SPEC-0001; the only endpoints that write)
        ├── dashboard.py   /api/dashboard
        ├── spending.py    /api/spending
        └── reports.py     /api/reports
```
The test conftest imports `app` from the top-level `main.py`, so keep that re-export.

Modules import with absolute paths from `server/` (`from app.data import orders`), which works because `server/` is on `sys.path` both when running the server and under the tests.

## Adding an endpoint
1. Put it in the router that owns its URL prefix, or create `app/routers/<area>.py` with `router = APIRouter(prefix="/api/<area>", tags=["<area>"])`.
2. Register a new router in the `include_router` loop in `app/main.py`.
3. Add a model to `app/models.py` and set `response_model`. The dashboard, spending and reports endpoints currently return untyped dicts.
4. Reuse `apply_filters` / `filter_by_month` for the standard filters rather than re-implementing them. A missing value or `'all'` means "don't filter". Category and status match case-insensitively, warehouse matches exactly.
5. For writes to the shared data and for request-field types (dates, floats), follow `.claude/rules/data.md`.

## Endpoints the client calls that don't exist yet
- `GET/POST /api/tasks`, `DELETE /api/tasks/{id}`, `PATCH /api/tasks/{id}` (toggle completion), used by the tasks UI in `client/src/App.vue`. These need a spec (`/specify`, or `/spec` for a quick draft).

## Security posture
Demo only: CORS allows `*` with credentials, and there's no auth and no rate limiting. Don't "fix" these unless asked.
