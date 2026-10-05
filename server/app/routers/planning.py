"""Demand forecasts and backlog. Neither endpoint takes filters."""
from typing import List

from fastapi import APIRouter

from app.data import backlog_items, demand_forecasts, purchase_orders
from app.models import BacklogItem, DemandForecast

router = APIRouter(prefix="/api", tags=["planning"])


@router.get("/demand", response_model=List[DemandForecast])
def get_demand_forecasts():
    """Get demand forecasts"""
    return demand_forecasts


@router.get("/backlog", response_model=List[BacklogItem])
def get_backlog():
    """Get backlog items with purchase order status"""
    # Add has_purchase_order flag to each backlog item
    result = []
    for item in backlog_items:
        item_dict = dict(item)
        # Check if this backlog item has a purchase order
        has_po = any(po["backlog_item_id"] == item["id"] for po in purchase_orders)
        item_dict["has_purchase_order"] = has_po
        result.append(item_dict)
    return result
