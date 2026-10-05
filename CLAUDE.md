# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Factory Inventory Management System demo: Vue 3 + Vite frontend, Python FastAPI backend, in-memory data loaded from JSON (no database, no real auth).

## Where guidance lives
This file covers the whole repo. More specific guidance loads only when relevant:

| File | Loaded when working on |
|---|---|
| `server/CLAUDE.md` | backend package layout, adding endpoints, missing endpoints |
| `client/CLAUDE.md` | frontend state, routing, API client |
| `.claude/rules/data.md` | `server/data/`, data loading, Pydantic models |
| `.claude/rules/testing.md` | `tests/` |
| `.claude/rules/i18n.md` | locales, currency, translated names |
| `.claude/rules/design-system.md` | `.vue` files |

Keep each fact in exactly one of these files; link to it rather than copying it.

*Why* the architecture is the way it is lives in `docs/adr/`. Read the relevant ADR before reversing one of those decisions, and add a new ADR (see `docs/adr/README.md`) when you make an architectural change.

*What* a feature will do is agreed in a spec in `docs/specs/` (`/spec <description>` drafts one). When implementing a spec, treat its API contract and acceptance criteria as the requirements. Don't build anything still listed under Open questions without asking.

## Tool rules
- **vue-expert subagent**: **MANDATORY** for creating or significantly modifying any `.vue` file.
- **code-reviewer** after significant changes; **security-auditor** for security review.
- **backend-api-test skill** when writing or modifying tests in `tests/backend/`.
- **GitHub MCP tools** (`mcp__github__*`, server defined in `.claude/mcp-config.json`, needs `GITHUB_PERSONAL_ACCESS_TOKEN`) for GitHub operations, except local branches: use `git checkout -b`.
- **Playwright MCP tools** (`mcp__playwright__*`, from `.mcp.json`) for browser testing.

## Commands

```bash
# Backend: http://localhost:8001, docs at /docs. server/ holds the only Python env.
cd server && uv venv && uv sync          # first time
cd server && uv run python main.py

# Frontend: http://localhost:3000/dashboard/
cd client && npm install                 # first time
cd client && npm run dev
cd client && npm run build               # the only check the client has (no linter, no tests)

# Backend tests (must run from server/; single-file/single-test forms in .claude/rules/testing.md)
cd server && uv run pytest ../tests -c ../tests/pytest.ini

# macOS/Linux: start/stop both services
./scripts/start.sh && ./scripts/stop.sh
```

## How the pieces connect
`client/src/api.js` calls relative `/api/*` URLs. The Vite dev server proxies `/api` to `localhost:8001` (`client/vite.config.js`), where a router in `server/app/routers/` filters in-memory data and validates it through Pydantic models. The frontend therefore only works through the Vite dev server, or a server that proxies `/api` the same way.

The four global filters (time period, warehouse, category, order status) are held in one client-side composable and sent as query params (`month`, `warehouse`, `category`, `status`). Every filtered endpoint applies them with the same two helpers in `server/app/filters.py`.

**Known gap:** the client already calls `/api/tasks`, which the backend doesn't implement yet (see `server/CLAUDE.md`).

## Business rules
- Revenue goals: $800K/month for a single month, $9.6M YTD across all months.
