# SPEC-0001: Purchase orders API

| | |
|---|---|
| **Status** | Approved (2026-10-05). Implemented on branch `feat/purchase-orders-api`; becomes Implemented when merged |
| **Owner** | |
| **Created** | 2026-10-05 |
| **Related** | ADR-0002, ADR-0007; follow-up listed in PR #1; commit 890756f, plus the date-rule change (see Decisions, D4) |

## Summary
Implement the two purchase-order endpoints that the client already calls but the backend didn't serve, so that a purchase order (PO) can be raised against a backlog item and `/api/backlog` reflects it. This spec covers the backend only. UI wiring is a follow-up.

## Problem
- `client/src/api.js` defined `createPurchaseOrder` (`POST /api/purchase-orders`) and `getPurchaseOrderByBacklogItem` (`GET /api/purchase-orders/{backlogItemId}`). Neither route existed, so both returned 404.
- `server/app/models.py` already defined `PurchaseOrder` and `CreatePurchaseOrderRequest`, but nothing used them.
- `server/data/purchase_orders.json` is `[]`, so `/api/backlog` always reported `has_purchase_order: false`.

## Goals
- Create a PO for an existing backlog item.
- Fetch all POs for a backlog item. A backlog item can have several POs (D1).
- `/api/backlog` reports `has_purchase_order: true` for an item once a PO exists for it.

## Non-goals
- UI for creating or viewing POs. No component calls either `api.js` function yet (see Follow-ups).
- Persisting POs across restarts (ADR-0002).
- Editing, cancelling, approving, rejecting or receiving POs, or any supplier master data.

## Decisions
All decided 2026-10-05.

| # | Question | Decision |
|---|---|---|
| D1 | One or several POs per backlog item? | **Several.** The GET returns a list (`[]` when there are none), and the `api.js` lookup is renamed to the plural. |
| D2 | If only one, should a second `POST` conflict or replace? | **Doesn't apply**, because several are allowed (D1). |
| D3 | ID format? | **Prefixed and sequential:** `PO-0001`, `PO-0002`, ... |
| D4 | Validate `expected_delivery_date`? Allow past dates? | **It must be a real `YYYY-MM-DD` date, and today or later.** This was first decided as "past dates allowed" and revised the same day, before merge. |
| D5 | Initial status and other states? | **`Pending`** on creation; the other states are **`Approved`** and **`Rejected`**. |

## API contract

| Method | Path | Query params | Request body | Response | Errors |
|---|---|---|---|---|---|
| POST | `/api/purchase-orders` | — | `CreatePurchaseOrderRequest` | **201** `PurchaseOrder` | 404 unknown `backlog_item_id`; 422 invalid body |
| GET | `/api/purchase-orders/{backlog_item_id}` | — | — | `List[PurchaseOrder]`, oldest first; `[]` if the item has none | 404 unknown `backlog_item_id` |

Neither endpoint takes the global filters, because POs have no warehouse, category or date dimension.

Request (`expected_delivery_date` must be today or later):
```json
{
  "backlog_item_id": "2",
  "supplier_name": "Northwind Motors",
  "quantity": 10,
  "unit_cost": 445.0,
  "expected_delivery_date": "2026-10-19",
  "notes": "Expedite"
}
```
Response (`id`, `status` and `created_date` are set by the server):
```json
{
  "id": "PO-0001",
  "backlog_item_id": "2",
  "supplier_name": "Northwind Motors",
  "quantity": 10,
  "unit_cost": 445.0,
  "expected_delivery_date": "2026-10-19",
  "status": "Pending",
  "created_date": "2026-10-05T14:03:00",
  "notes": "Expedite"
}
```

## Data and models
- **Request constraints** (`CreatePurchaseOrderRequest`): `quantity > 0`, `unit_cost >= 0`, and `supplier_name` not empty. Surrounding whitespace is trimmed, so `"   "` counts as empty and is rejected. Pydantic returns the 422.
- **Server-set fields:** the request model has no `id`, `status` or `created_date`, and any extra fields the client sends are ignored. A body containing `"status": "Approved"` still creates a `Pending` PO.
- **`expected_delivery_date`** (D4) stays a string in both models, so it's stored and returned exactly as sent. It's validated by two annotated types in `server/app/models.py`:
  ```python
  IsoDate = Annotated[str, StringConstraints(strict=True, pattern=r"^\d{4}-\d{2}-\d{2}$"),
                      AfterValidator(_real_date)]        # date.fromisoformat must succeed
  FutureIsoDate = Annotated[IsoDate, AfterValidator(_not_in_past)]   # >= date.today()
  ```
  - We tested each part through a real FastAPI endpoint on pydantic 2.13 / Python 3.12:
    - **The pattern:** `fromisoformat` alone also accepts `"20251020"`.
    - **`fromisoformat`:** the pattern alone would accept `"2025-02-30"`.
    - **`strict=True` on the string:** this rejects the number `1760918400`.
    - **Not a `date` type:** a lax `date` field accepts Unix timestamps and `"2025-10-20T00:00:00"`. A `date` with `Field(strict=True)` rejects every request, because FastAPI validates the already-parsed Python values, not raw JSON.
  - **"Today"** is the **server's local date**, checked on each request, so today itself is accepted. A client in a timezone ahead of the server could see its "today" rejected for a few hours. That's acceptable for this demo.
  - `IsoDate` stays available for date fields that may be in the past.
- **Status** (D5): `PurchaseOrder.status` is `Literal["Pending", "Approved", "Rejected"]`. Nothing in this spec moves a PO out of `Pending`.
- **Store:** POs are appended to `app.data.purchase_orders`, the one intended exception to the read-only rule. They go into that **same list object**; the name is never rebound, because `planning.get_backlog` holds the list by reference.
- **Persistence:** POs are lost on restart, which ADR-0002 accepts for this demo. `purchase_orders.json` stays `[]`.
- **IDs** (D3): generated as `f"PO-{len(purchase_orders) + 1:04d}"`. Counting the list is safe because POs are never deleted. If deletion is added later, this needs a separate counter. Numbers past 9999 grow to 5 digits.

## Implementation
- **Router:** `server/app/routers/purchase_orders.py` (`prefix="/api/purchase-orders"`, tag `purchase-orders`), registered in `server/app/main.py` (ADR-0007). Both endpoints share `_require_backlog_item`, which returns 404 for an unknown item.
- **Models:** `IsoDate`, `FutureIsoDate`, `PurchaseOrderStatus` and the request constraints, in `server/app/models.py`.
- **Created date:** `datetime.now().isoformat(timespec="seconds")`, the server's local time with no timezone suffix, matching the format of other dates in the data.
- **Frontend:** `getPurchaseOrderByBacklogItem` was renamed to `getPurchaseOrdersByBacklogItem` in `client/src/api.js`. It had no callers.
- **Docs:** `server/CLAUDE.md` lists the router and the in-place mutation and `IsoDate` rules, and purchase orders were removed from the known-gap notes.

## Architecture impact
None. This follows ADR-0007 (one router per area) and ADR-0002 (in-memory store). It's the first endpoint that writes to that store, which ADR-0002 already anticipates.

## Edge cases and errors
- Unknown `backlog_item_id` → 404 on both endpoints, and nothing is appended.
- Several POs for the same backlog item are all kept and all returned, and `has_purchase_order` is `true` if there is at least one.
- A known backlog item with no POs → `200 []`, not 404.
- `expected_delivery_date`:
  - Today or any later real date → accepted, including leap days.
  - Before today → 422 with `"date must be today or later"`.
  - An impossible date, a format other than `YYYY-MM-DD`, a timestamp or a datetime → 422.
- After a server restart, POs disappear and `has_purchase_order` reverts to `false`. This is expected.

## Test plan
`tests/backend/test_purchase_orders.py`: 29 tests in `TestPurchaseOrderEndpoints`.
- **Fixtures:**
  - An autouse fixture restores `app.data.purchase_orders` in place after each test, using slice assignment so the list object stays the same.
  - Date helpers (`days_from_today`, `next_leap_day`) keep the tests valid as time passes. No fixed future dates are used.
- **Create:** 201 with the server-set fields; sequential IDs; client-sent `status` and `id` ignored; unknown backlog item gives 404 and leaves the store unchanged.
- **Validation:** 422 for `quantity` 0 or negative, negative `unit_cost`, empty or blank `supplier_name`, and a missing field.
- **Delivery date:**
  - 422 for impossible dates (`2025-02-30`, `2025-02-29`, `2025-13-01`) and wrong formats (`2025/10/20`, `20251020`, a datetime, a timestamp, `""`, `null`).
  - 422 with the "today or later" message for yesterday and `2020-01-01`.
  - 201, with the date echoed back unchanged, for today, a year ahead and the next Feb 29.
- **Lookup:** created PO returned; several POs returned oldest first; `[]` for an item with none; 404 for an unknown item.
- **Backlog:** `has_purchase_order` flips for that item only.

## Acceptance criteria
Checked 2026-10-05. The full test suite ran in-process. The live checks ran against the running backend: through the Vite proxy for the first implementation, and directly on :8001 after D4 changed, because the dev server had stopped by then.
- [x] `POST /api/purchase-orders` with the example body returns 201 and a `PurchaseOrder` with `status`, `id` and `created_date` set. `status` is `"Pending"`, even if the body tries to send another status. On a fresh server the first `id` is `PO-0001` and the second is `PO-0002`.
- [x] Afterwards, `GET /api/backlog` shows `has_purchase_order: true` for item `"2"` and `false` for every other item.
- [x] After two `POST`s for item `"2"`, `GET /api/purchase-orders/2` returns a list of both, oldest first.
- [x] `GET /api/purchase-orders/1` returns `200 []`, and `GET /api/purchase-orders/999` returns 404.
- [x] `POST` with `backlog_item_id: "999"` returns 404, and `quantity: 0` returns 422.
- [x] `POST` with `expected_delivery_date` of `"2025-02-30"`, `1760918400`, yesterday or `"2020-01-01"` returns 422. Yesterday's message says "today or later". Today's date returns 201 and is echoed back unchanged.
- [x] `api.js` exposes `getPurchaseOrdersByBacklogItem`, and the singular name is gone.
- [x] The new tests pass, and the existing 40 still pass: 69/69. Everything existing is unchanged: all 2,143 responses are identical, and the OpenAPI change only adds 2 paths and 2 schemas.
- [x] `server/CLAUDE.md` no longer lists these endpoints as missing.

## Follow-ups
- Approve or reject a PO (for example `PATCH /api/purchase-orders/{id}` with `{"status": ...}`). That needs its own spec for which transitions are allowed, and for whether a rejected PO still counts towards `has_purchase_order`.
- UI: a "Raise PO" action and PO details in `BacklogDetailModal.vue` (via the vue-expert subagent), with strings in all three locales. The date picker should default to today or later, to match D4.
- `/api/tasks`, the other set of endpoints the client calls that doesn't exist, which needs its own spec.
