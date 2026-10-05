# Architecture Decision Records

Each file records one significant decision: the context, what was decided and the consequences. See [ADR-0001](0001-record-architecture-decisions.md) for why and how we keep them.

| ADR | Decision | Status |
|---|---|---|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-in-memory-json-data-store.md) | Serve data from JSON files held in memory | Accepted |
| [0003](0003-relative-api-urls-via-dev-proxy.md) | Frontend calls the API through relative `/api` URLs and the Vite proxy | Accepted |
| [0004](0004-hash-history-routing.md) | Use hash-history routing | Accepted |
| [0005](0005-module-level-singleton-composables.md) | Share client state through module-level composables | Accepted |
| [0006](0006-locale-driven-currency.md) | Store amounts in USD; derive display currency from locale | Accepted |
| [0007](0007-backend-package-with-routers.md) | Split the backend into an `app/` package with one router per area | Accepted |
| [0008](0008-tests-use-server-environment.md) | Backend tests run in the server's uv environment | Accepted |
| [0009](0009-path-scoped-claude-guidance.md) | Split Claude Code guidance into path-scoped files | Accepted |

**Provenance.** ADRs 0002, 0005, 0006 and 0008 record decisions that existed before these records were written. Their *context* is inferred from the code, not from the original authors, and each says so. ADRs 0003 and 0004 come from commit messages. ADRs 0007 and 0009 were written alongside the change they describe.

## Adding an ADR
1. Copy [template.md](template.md) to `NNNN-short-title.md`, using the next number.
2. Fill it in and add a row to the table above.
3. Never rewrite an accepted ADR's decision. To change course, write a new ADR and set the old one's status to `Superseded by ADR-NNNN`.
