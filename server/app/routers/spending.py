from fastapi import APIRouter

from app.data import category_spending, monthly_spending, recent_transactions, spending_summary

router = APIRouter(prefix="/api/spending", tags=["spending"])


@router.get("/summary")
def get_spending_summary():
    """Get spending summary statistics"""
    return spending_summary


@router.get("/monthly")
def get_monthly_spending():
    """Get monthly spending breakdown"""
    return monthly_spending


@router.get("/categories")
def get_category_spending():
    """Get spending by category"""
    return category_spending


@router.get("/transactions")
def get_recent_transactions():
    """Get recent transactions"""
    return recent_transactions
