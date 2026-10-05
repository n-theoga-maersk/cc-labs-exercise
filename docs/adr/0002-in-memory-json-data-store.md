# 0002. Serve data from JSON files held in memory

- **Status:** Accepted
- **Date:** Predates this record; documented 2026-10-05
- **Source:** Inferred from code (`server/app/data.py`, README "Important Caveat")

## Context
The application is a demo of factory operations. It needs realistic-looking inventory, orders, forecasts and spending data, and must start with nothing more than `uv sync`. The README states plainly that it is not production-ready and would need "database integration, user authentication, and security hardening" first.

## Decision
Keep all data in JSON files under `server/data/`. `server/app/data.py` loads each file once at import into module-level Python objects, which the routers read directly. All filtering and aggregation happens in Python over those lists. There is no database.

## Consequences
- Setup is trivial and the API is fast, because everything is an in-memory list scan.
- Any write lasts only until the next restart. This matters for the planned purchase-order endpoint, which is meant to append to `purchase_orders`.
- Shared objects are returned by reference, so handlers must not change them in place.
- The JSON shape and the Pydantic models in `server/app/models.py` must be kept in step by hand.
- Data covers 2025 only, and `QUARTER_MAP` hard-codes 2025 quarters.
- The files are read as UTF-8 explicitly. The platform default (cp1252 on Windows) garbled non-ASCII product names, which was fixed in PR #1.
- Moving to a real database would replace `data.py` and most router bodies, but the routers' URLs and response models could stay the same.
