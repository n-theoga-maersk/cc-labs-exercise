# SPEC-NNNN: Feature name

| | |
|---|---|
| **Status** | Draft <!-- Draft → Approved → Implemented, or Abandoned --> |
| **Owner** | <!-- GitHub handle --> |
| **Created** | YYYY-MM-DD |
| **Related** | <!-- ADRs, PRs, issues, e.g. ADR-0002, #12 --> |

## Summary
<!-- Two or three sentences: what changes, for whom, and why now. -->

## Problem
<!-- What is broken, missing or painful today? Cite evidence: file paths, endpoints, screenshots, user reports. -->

## Goals
- <!-- Each goal should be checkable by an acceptance criterion below. -->

## Non-goals
- <!-- Things a reader might reasonably expect that this spec deliberately leaves out. -->

## User-facing behaviour
<!--
Describe what the user sees and does. Cover, where relevant:
- Which view or component changes (routes are hash-based, e.g. /dashboard/#/orders; see ADR-0004).
- How the four global filters (period, warehouse, category, status) affect it. Say explicitly if they don't.
- Loading, empty and error states.
- New UI strings: they must be added to en, ja AND pt_BR (client/src/locales/).
- Money: amounts are USD from the API and shown via client/src/utils/currency.js (ADR-0006).
Delete this section for backend-only work.
-->

## API contract
<!-- One row per new or changed endpoint. Mark changed endpoints as such: existing behaviour is a contract. -->

| Method | Path | Query params | Request body | Response | Errors |
|---|---|---|---|---|---|
| GET | `/api/...` | `warehouse`, `category`, `status`, `month` (standard filters; `'all'` or missing = no filter) | — | `List[Model]` | 404 if ... |

<!-- Give a JSON example of each request and response. -->

## Data and models
<!--
- JSON files in server/data/ that are added or changed, with an example record.
- Pydantic models added or changed in server/app/models.py. Prefer a response_model over an untyped dict.
- Persistence: data is in memory and resets on restart (ADR-0002). Say whether that's acceptable here.
- Shared objects in server/app/data.py are read-only, except for intended appends. Name any you append to.
-->

## Implementation outline
<!--
Backend (ADR-0007):
- Router: existing server/app/routers/<area>.py, or a new one registered in server/app/main.py.
- Reuse apply_filters / filter_by_month / quarter_for from server/app/filters.py.

Frontend:
- api.js function(s); never hard-code a backend host (ADR-0003).
- Views/components touched. Any .vue work goes through the vue-expert subagent.
- Shared state: an existing composable, or a new module-level one (ADR-0005).
-->

## Architecture impact
<!--
Does this introduce, change or contradict an architectural decision?
- No: say "None", and why.
- Yes: name the ADR it affects and list the new ADR as an acceptance criterion.
-->

## Edge cases and errors
- <!-- Invalid IDs, unknown filter values, empty data, duplicates, concurrent requests, restart mid-flow. -->

## Test plan
<!--
- Backend: test file and test names in tests/backend/ (use the backend-api-test skill). Cover the happy path, each filter, 404/422, and the invariants.
- Changes to existing endpoints: snapshot full responses before and after (see ADR-0007), not just the pytest suite.
- Frontend: manual or Playwright steps against http://localhost:3000/dashboard/, in each locale if UI text changes.
-->

## Acceptance criteria
- [ ] <!-- Observable and verifiable, e.g. "GET /api/x?warehouse=Tokyo returns only Tokyo rows". -->
- [ ] Backend tests added and passing: `cd server && uv run pytest ../tests -c ../tests/pytest.ini`
- [ ] Guidance updated if a documented fact changed (CLAUDE.md files, `.claude/rules/`)

## Open questions
- <!-- Anything undecided. A spec can't move to Approved while an item here would change the API contract. -->

## Follow-ups
- <!-- Related work discovered while writing this spec but out of scope. -->
