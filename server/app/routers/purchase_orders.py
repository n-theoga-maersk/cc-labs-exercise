"""Purchase orders raised against backlog items (SPEC-0001). Stored in memory only (ADR-0002)."""
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException

from app.data import backlog_items, purchase_orders
from app.models import CreatePurchaseOrderRequest, PurchaseOrder

router = APIRouter(prefix="/api/purchase-orders", tags=["purchase-orders"])


def _require_backlog_item(backlog_item_id: str) -> None:
    if not any(item["id"] == backlog_item_id for item in backlog_items):
        raise HTTPException(status_code=404, detail="Backlog item not found")


@router.post("", response_model=PurchaseOrder, status_code=201)
def create_purchase_order(request: CreatePurchaseOrderRequest):
    """Create a purchase order for a backlog item; new orders always start as Pending"""
    _require_backlog_item(request.backlog_item_id)

    purchase_order = {
        **request.model_dump(),
        # Counting is safe while POs are never deleted
        "id": f"PO-{len(purchase_orders) + 1:04d}",
        "status": "Pending",
        "created_date": datetime.now().isoformat(timespec="seconds"),
    }
    # Append to the shared list (never rebind it): planning.get_backlog reads this same object
    purchase_orders.append(purchase_order)
    return purchase_order


@router.get("/{backlog_item_id}", response_model=List[PurchaseOrder])
def get_purchase_orders_by_backlog_item(backlog_item_id: str):
    """Get all purchase orders for a backlog item, oldest first; empty if it has none"""
    _require_backlog_item(backlog_item_id)
    return [po for po in purchase_orders if po["backlog_item_id"] == backlog_item_id]
