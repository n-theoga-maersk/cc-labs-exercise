# SPEC-0001: Purchase orders API

| | |
|---|---|
| **Status** | Draft |
| **Owner** | |
| **Created** | 2026-10-05 |
| **Related** | ADR-0002, ADR-0007; follow-up listed in PR #1 |

## Summary
Implement the two purchase-order endpoints that the client already calls but the backend doesn't serve, so that a purchase order (PO) can be raised against a backlog item and `/api/backlog` reflects it. This spec covers the backend only. UI wiring is a follow-up.

## Problem
- `client/src/api.js` defines `createPurchaseOrder` (`POST /api/purchase-orders`) and `getPurchaseOrderByBacklogItem` (`GET /api/purchase-orders/{backlogItemId}`). Neither route exists, so both return 404.
- `server/app/models.py` already defines `PurchaseOrder` and `CreatePurchaseOrderRequest`, but nothing uses them.
- `server/data/purchase_orders.json` is `[]`, so `/api/backlog` always reports `has_purchase_order: false`.

## Goals
- Create a PO for an existing backlog item.
- Fetch all POs for a backlog item. A backlog item can have several POs (decided 2026-10-05, Q1).
- `/api/backlog` reports `has_purchase_order: true` for an item once a PO exists for it.

## Non-goals
- UI for creating or viewing POs. Today no component calls either `api.js` function (see Follow-ups).
- Persisting POs across restarts (ADR-0002).
- Editing, cancelling or receiving POs, or any supplier master data.

## API contract

| Method | Path | Query params | Request body | Response | Errors |
|---|---|---|---|---|---|
| POST | `/api/purchase-orders` | — | `CreatePurchaseOrderRequest` | **201** `PurchaseOrder` | 404 unknown `backlog_item_id`; 422 invalid body |
| GET | `/api/purchase-orders/{backlog_item_id}` | — | — | `List[PurchaseOrder]`, oldest first; `[]` if the item has none | 404 unknown `backlog_item_id` |

Neither endpoint takes the global filters, because POs have no warehouse, category or date dimension.

Request:
```json
{
  "backlog_item_id": "2",
  "supplier_name": "Northwind Motors",
  "quantity": 10,
  "unit_cost": 445.0,
  "expected_delivery_date": "2025-10-20",
  "notes": "Expedite"
}
```
Response (fields `id`, `status` and `created_date` are set by the server):
```json
{
  "id": "PO-0001",
  "backlog_item_id": "2",
  "supplier_name": "Northwind Motors",
  "quantity": 10,
  "unit_cost": 445.0,
  "expected_delivery_date": "2025-10-20",
  "status": "Pending",
  "created_date": "2026-10-05T14:03:00",
  "notes": "Expedite"
}
```

## Data and models
- **Models:** reuse `PurchaseOrder` and `CreatePurchaseOrderRequest` unchanged in shape. Add constraints to the request: `quantity > 0`, `unit_cost >= 0`, and `supplier_name` not empty. The 422 then comes from Pydantic.
- **Store:** append to `app.data.purchase_orders`, which is the one intended exception to the read-only rule. Append to that **same list object**; don't rebind the name. `planning.get_backlog` imported the list by reference, and would never see a new list.
- **Persistence:** POs are lost on restart, which ADR-0002 accepts for this demo. `purchase_orders.json` stays `[]`.
- **IDs:** `PO-` plus a sequential number, zero-padded to 4 digits (`PO-0001`, `PO-0002`, ...), generated as `f"PO-{len(purchase_orders) + 1:04d}"` (decided 2026-10-05, Q3). Counting the list is safe because POs are never deleted. If deletion is added later, this needs a separate counter. Numbers past 9999 simply grow to 5 digits.

## Implementation outline
- New router `server/app/routers/purchase_orders.py`: `APIRouter(prefix="/api/purchase-orders", tags=["purchase-orders"])`, added to the `include_router` loop in `server/app/main.py` (ADR-0007).
- Look up the backlog item in `app.data.backlog_items` to validate `backlog_item_id`.
- Frontend: rename `getPurchaseOrderByBacklogItem` to `getPurchaseOrdersByBacklogItem` in `client/src/api.js`, because it now returns a list. Nothing calls it yet, so no other file changes. `createPurchaseOrder` already matches.

## Architecture impact
None. This follows ADR-0007 (one router per area) and ADR-0002 (in-memory store). It is the first endpoint that writes to that store, which ADR-0002 already anticipates.

## Edge cases and errors
- Unknown `backlog_item_id` → 404 on both endpoints, and nothing is appended.
- Several POs for the same backlog item are all kept and all returned, and `has_purchase_order` is `true` if there is at least one.
- A known backlog item with no POs → `200 []`, not 404.
- `expected_delivery_date` in the past or badly formatted: not validated today *(see Q4)*.
- After a server restart, POs disappear and `has_purchase_order` reverts to `false`. This is expected.

## Test plan
New file `tests/backend/test_purchase_orders.py` (use the backend-api-test skill):
- `test_create_purchase_order`: 201, server fields are set, and the body round-trips.
- `test_create_purchase_order_unknown_backlog_item`: 404, and the store is unchanged.
- `test_create_purchase_order_invalid_body`: 422 for `quantity: 0` and for a missing field.
- `test_get_purchase_orders_by_backlog_item`: returns a list containing what was created.
- `test_multiple_purchase_orders_per_backlog_item`: two POs for one item, and both are returned, oldest first.
- `test_get_purchase_orders_none`: `200 []` for a known backlog item with no PO.
- `test_get_purchase_orders_unknown_backlog_item`: 404.
- `test_backlog_reflects_purchase_order`: `has_purchase_order` flips to `true` for that item only.

The module-level store is shared by every test. Add a fixture that snapshots and restores `app.data.purchase_orders`, so the tests stay independent.

## Acceptance criteria
- [ ] `POST /api/purchase-orders` with the example body returns 201 and a `PurchaseOrder` with `status`, `id` and `created_date` set. On a fresh server the first `id` is `PO-0001` and the second is `PO-0002`.
- [ ] Afterwards, `GET /api/backlog` shows `has_purchase_order: true` for item `"2"` and `false` for every other item.
- [ ] After two `POST`s for item `"2"`, `GET /api/purchase-orders/2` returns a list of both, oldest first.
- [ ] `GET /api/purchase-orders/1` returns `200 []`, and `GET /api/purchase-orders/999` returns 404.
- [ ] `POST` with `backlog_item_id: "999"` returns 404, and `quantity: 0` returns 422.
- [ ] `api.js` exposes `getPurchaseOrdersByBacklogItem`, and the singular name is gone.
- [ ] The new tests pass, and the existing 40 still pass: `cd server && uv run pytest ../tests -c ../tests/pytest.ini`
- [ ] `server/CLAUDE.md` no longer lists these endpoints as missing.

## Open questions
1. ~~One or many POs per backlog item?~~ **Resolved 2026-10-05: several.** The GET returns a list (`[]` when there are none), and the `api.js` function becomes plural.
2. ~~If only one is allowed, should a second `POST` return 409 or replace?~~ **No longer applies** (see Q1).
3. ~~Plain sequence or prefixed IDs?~~ **Resolved 2026-10-05: prefixed**, `PO-0001` (see Data and models).
4. Should `expected_delivery_date` be validated as an ISO date, and must it be in the future?
5. Initial `status`: is `"Pending"` right, and what are the other states? This is out of scope here, but it affects the model's documentation.

## Follow-ups
- UI: a "Raise PO" action and PO details in `BacklogDetailModal.vue` (via the vue-expert subagent), with strings in all three locales.
- `/api/tasks`, the other set of endpoints the client calls that doesn't exist, which needs its own spec.
