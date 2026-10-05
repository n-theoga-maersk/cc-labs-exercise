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
- Tests that write to the in-memory store must restore it in place afterwards, and compare against the starting state rather than assume it's empty. See the autouse `baseline` fixture in `test_purchase_orders.py`.
- Compute dates relative to `date.today()` inside the test body, never in `parametrize` arguments, which are evaluated once at collection.
- `tests/README.md` is out of date: it lists a `test_orders.py` that doesn't exist and claims 51 tests (there are 72: 40 for the original endpoints, 32 for purchase orders). Orders endpoints have no dedicated test file.
