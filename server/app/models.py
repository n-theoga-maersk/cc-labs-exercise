"""Pydantic models for typed API responses and request bodies."""
from datetime import date
from typing import Annotated, List, Literal, Optional

from pydantic import AfterValidator, BaseModel, Field, StringConstraints


def _real_date(v: str) -> str:
    date.fromisoformat(v)  # ValueError on impossible dates such as 2025-02-30 -> 422
    return v


# A YYYY-MM-DD string that is a real calendar date, kept as a string so it round-trips unchanged.
# The pattern is needed because fromisoformat also accepts "20251020"; strict rejects numbers
# (a plain `date` field would accept Unix timestamps). See SPEC-0001.
IsoDate = Annotated[str, StringConstraints(strict=True, pattern=r"^\d{4}-\d{2}-\d{2}$"),
                    AfterValidator(_real_date)]


def _not_in_past(v: str) -> str:
    # "Today" is the server's local date, evaluated per request
    if date.fromisoformat(v) < date.today():
        raise ValueError("date must be today or later")
    return v


# An IsoDate that is today or later
FutureIsoDate = Annotated[IsoDate, AfterValidator(_not_in_past)]

PurchaseOrderStatus = Literal["Pending", "Approved", "Rejected"]


class InventoryItem(BaseModel):
    id: str
    sku: str
    name: str
    category: str
    warehouse: str
    quantity_on_hand: int
    reorder_point: int
    unit_cost: float
    location: str
    last_updated: str


class Order(BaseModel):
    id: str
    order_number: str
    customer: str
    items: List[dict]
    status: str
    order_date: str
    expected_delivery: str
    total_value: float
    actual_delivery: Optional[str] = None
    warehouse: Optional[str] = None
    category: Optional[str] = None


class DemandForecast(BaseModel):
    id: str
    item_sku: str
    item_name: str
    current_demand: int
    forecasted_demand: int
    trend: str
    period: str


class BacklogItem(BaseModel):
    id: str
    order_id: str
    item_sku: str
    item_name: str
    quantity_needed: int
    quantity_available: int
    days_delayed: int
    priority: str
    has_purchase_order: Optional[bool] = False


class PurchaseOrder(BaseModel):
    id: str
    backlog_item_id: str
    supplier_name: str
    quantity: int
    unit_cost: float
    expected_delivery_date: str
    status: PurchaseOrderStatus
    created_date: str
    notes: Optional[str] = None


class CreatePurchaseOrderRequest(BaseModel):
    """Client-supplied fields only: id, status and created_date are set by the server."""
    backlog_item_id: str
    supplier_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    quantity: int = Field(gt=0)
    unit_cost: float = Field(ge=0, allow_inf_nan=False)
    expected_delivery_date: FutureIsoDate
    notes: Optional[str] = None
