---
paths:
  - "server/data/**"
  - "server/app/data.py"
  - "server/app/models.py"
  - "server/generate_data.py"
---

# Mock data

- `server/app/data.py` loads every `server/data/*.json` file **once at import** into module-level objects that the routers import directly. Restarting the server resets everything, and edits to a JSON file need a restart to show.
- Treat those objects as read-only and build new lists or dicts instead (`get_backlog` uses `dict(item)`). The only intended in-place change is appending to `purchase_orders`, done by `server/app/routers/purchase_orders.py` under its lock. Always mutate that same list object, and never rebind the name: other routers imported it by reference and would keep seeing the old list.
- Request-model types in `server/app/models.py`:
  - Date-only fields use `IsoDate`, a real `YYYY-MM-DD` string, or `FutureIsoDate` (today or later, server-local). Don't use `date`: lax mode accepts Unix timestamps, and `Field(strict=True)` rejects every FastAPI body.
  - Float inputs need `allow_inf_nan=False`. JSON bodies can contain `NaN`/`Infinity`, and the app's 422 handler in `server/app/main.py` keeps such rejections from becoming 500s.
- Real values, which tests and the UI rely on:
  - Warehouses: `San Francisco`, `London`, `Tokyo`.
  - Categories: `Circuit Boards`, `Sensors`, `Actuators`, `Controllers`, `Power Supplies`.
  - Order statuses: `Delivered`, `Shipped`, `Processing`, `Backordered`.
  - 250 orders across every month of 2025.

  Keep these consistent across files.
- Inventory, orders, demand and backlog are validated against models in `server/app/models.py`, so when a JSON shape changes, update the model too or responses will fail. Spending and transactions are returned untyped.
- Dates are ISO strings (`2025-01-08T10:19:00`). Month filtering is a substring match on `order_date`. `QUARTER_MAP` in `server/app/filters.py` hard-codes 2025, so data for other years silently drops out of quarter filters and quarterly reports.
- **Don't run `server/generate_data.py`.** It is stale: it only rewrites `orders.json`, with unseeded random data, warehouses `A/B/C` and categories that exist nowhere else.
