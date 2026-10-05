# Testing

## Building from a spec — RED-GREEN (YOU MUST)
When implementing a feature that has a spec in `docs/specs/`, work test-first against its **Acceptance criteria**, one criterion at a time:

1. **Write the test.** Take the next unmet acceptance criterion and write a test that captures it. Write no implementation yet.
2. **RED.** Run that test and **show the user the failing output**. It must fail for the right reason: the behaviour is missing (for example, a 404 for a route that doesn't exist yet, or a wrong value). It must not fail because of a typo, an import error, a bad fixture or a broken test. If it fails for the wrong reason, fix the test and run it again before going on.
3. **GREEN.** Write the minimum code that makes it pass. Run that test, then the **full suite** for every side you touched (commands in the root `CLAUDE.md`). Everything must pass, with no regressions.
4. **Refactor** if it's useful, re-running the suite to keep it green. Then go back to step 1 with the next criterion.

**NEVER modify a test just to make it pass.** If a criterion is ambiguous, or a test looks wrong, or the spec and the code disagree, **STOP and ask the user** before changing the test, the spec or the criterion.

## Backend tests

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
