---
paths:
  - "tests/**"
---

# Backend tests

Use the **backend-api-test** skill when writing tests. The full-suite command is in the root `CLAUDE.md`. Tests must run with the server's uv environment, because `tests/` has none and `cd tests && uv run pytest` fails. To narrow a run:

```bash
cd server
uv run pytest ../tests/backend/test_inventory.py -c ../tests/pytest.ini                     # file
uv run pytest "../tests/backend/test_inventory.py::TestInventoryEndpoints::test_get_all_inventory" -c ../tests/pytest.ini
```

- `tests/backend/conftest.py` puts `server/` on `sys.path` and wraps `main.app` in a `TestClient` fixture named `client`.
- Most tests assert on structure and invariants, not exact values. When refactoring, also compare full responses before and after.
- `tests/README.md` is out of date: it lists a `test_orders.py` that doesn't exist and claims 51 tests (there are 40). Orders endpoints have no dedicated test file.
