"""Shared query-param filtering. A missing value or 'all' means "don't filter"."""
from typing import Optional

# Quarter mapping for date filtering
QUARTER_MAP = {
    'Q1-2025': ['2025-01', '2025-02', '2025-03'],
    'Q2-2025': ['2025-04', '2025-05', '2025-06'],
    'Q3-2025': ['2025-07', '2025-08', '2025-09'],
    'Q4-2025': ['2025-10', '2025-11', '2025-12']
}


def quarter_for(date: str) -> Optional[str]:
    """Return the QUARTER_MAP key containing this date, or None if it isn't in a known quarter"""
    for quarter, months in QUARTER_MAP.items():
        if any(m in date for m in months):
            return quarter
    return None


def filter_by_month(items: list, month: Optional[str]) -> list:
    """Filter items by month/quarter based on order_date field"""
    if not month or month == 'all':
        return items

    if month.startswith('Q'):
        # Handle quarters
        if month in QUARTER_MAP:
            return [item for item in items if quarter_for(item.get('order_date', '')) == month]
    else:
        # Direct month match
        return [item for item in items if month in item.get('order_date', '')]

    return items


def apply_filters(items: list, warehouse: Optional[str] = None, category: Optional[str] = None,
                  status: Optional[str] = None) -> list:
    """Apply common filters to a list of items"""
    filtered = items

    if warehouse and warehouse != 'all':
        filtered = [item for item in filtered if item.get('warehouse') == warehouse]

    if category and category != 'all':
        filtered = [item for item in filtered if item.get('category', '').lower() == category.lower()]

    if status and status != 'all':
        filtered = [item for item in filtered if item.get('status', '').lower() == status.lower()]

    return filtered
