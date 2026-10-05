# 0008. Backend tests run in the server's uv environment

- **Status:** Accepted
- **Date:** Predates this record; documented 2026-10-05
- **Source:** Inferred from layout (`server/pyproject.toml`, `tests/pytest.ini`, `tests/backend/conftest.py`)

## Context
Tests live in a top-level `tests/` directory, separate from `server/`. The test dependencies (pytest, pytest-asyncio, httpx, pytest-cov) are declared as dev dependencies in `server/pyproject.toml`. `tests/` has no project file of its own, and `conftest.py` puts `server/` on `sys.path` to import `main.app`.

## Decision
Keep one Python environment, `server/.venv`, and run the tests from it:

```bash
cd server && uv run pytest ../tests -c ../tests/pytest.ini
```

## Consequences
- One lockfile and one environment to keep in sync with the app.
- `cd tests && uv run pytest`, which `tests/README.md` documents, **doesn't work**: uv finds no project and pytest isn't installed. The working command is recorded in the root `CLAUDE.md` and the `backend-api-test` skill.
- Coverage is measured with `--cov=app` now that the code lives in `server/app/` (ADR-0007).
- Alternatives for later: give `tests/` its own `pyproject.toml`, or move the tests under `server/`. Either would make the shorter command work, but needs its own ADR.
