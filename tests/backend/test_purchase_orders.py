"""
Tests for purchase order API endpoints (SPEC-0001).
"""
from datetime import date, timedelta

import pytest

import app.data


def days_from_today(days):
    """ISO date relative to today, so tests don't go stale (delivery dates can't be in the past)."""
    return (date.today() + timedelta(days=days)).isoformat()


def next_leap_day():
    """The next Feb 29 on or after today."""
    year = date.today().year
    while True:
        try:
            leap = date(year, 2, 29)
            if leap >= date.today():
                return leap.isoformat()
        except ValueError:
            pass
        year += 1


@pytest.fixture(autouse=True)
def restore_purchase_orders():
    """POs live in a module-level list shared by every test; restore it in place after each test.

    Slice assignment keeps the same list object, which the routers hold by reference.
    """
    saved = list(app.data.purchase_orders)
    yield
    app.data.purchase_orders[:] = saved


@pytest.fixture
def po_body():
    """Valid create request for backlog item "2"."""
    return {
        "backlog_item_id": "2",
        "supplier_name": "Northwind Motors",
        "quantity": 10,
        "unit_cost": 445.0,
        "expected_delivery_date": days_from_today(14),
        "notes": "Expedite",
    }


class TestPurchaseOrderEndpoints:
    """Test suite for purchase-order endpoints."""

    def test_create_purchase_order(self, client, po_body):
        """Test creating a purchase order sets server fields and echoes the body."""
        response = client.post("/api/purchase-orders", json=po_body)
        assert response.status_code == 201

        po = response.json()
        for field, value in po_body.items():
            assert po[field] == value
        assert po["id"] == "PO-0001"
        assert po["status"] == "Pending"
        assert "T" in po["created_date"]

    def test_create_purchase_order_ids_are_sequential(self, client, po_body):
        """Test that IDs follow the PO-NNNN sequence."""
        first = client.post("/api/purchase-orders", json=po_body).json()
        second = client.post("/api/purchase-orders", json=po_body).json()
        assert (first["id"], second["id"]) == ("PO-0001", "PO-0002")

    def test_create_purchase_order_ignores_client_status(self, client, po_body):
        """Test that the client cannot choose the initial status or id."""
        response = client.post(
            "/api/purchase-orders", json={**po_body, "status": "Approved", "id": "HACK"}
        )
        assert response.status_code == 201
        assert response.json()["status"] == "Pending"
        assert response.json()["id"] == "PO-0001"

    def test_create_purchase_order_unknown_backlog_item(self, client, po_body):
        """Test creating a PO for a backlog item that doesn't exist."""
        response = client.post(
            "/api/purchase-orders", json={**po_body, "backlog_item_id": "999"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
        assert app.data.purchase_orders == []

    @pytest.mark.parametrize("override", [
        {"quantity": 0},
        {"quantity": -5},
        {"unit_cost": -1},
        {"supplier_name": ""},
        {"supplier_name": "   "},
    ])
    def test_create_purchase_order_invalid_body(self, client, po_body, override):
        """Test that invalid field values are rejected."""
        response = client.post("/api/purchase-orders", json={**po_body, **override})
        assert response.status_code == 422
        assert app.data.purchase_orders == []

    def test_create_purchase_order_missing_field(self, client, po_body):
        """Test that a missing required field is rejected."""
        del po_body["supplier_name"]
        response = client.post("/api/purchase-orders", json=po_body)
        assert response.status_code == 422

    @pytest.mark.parametrize("bad_date", [
        "2025-02-30", "2025-02-29", "2025-13-01", "2025/10/20", "20251020",
        "2025-10-20T00:00:00", 1760918400, "", None,
    ])
    def test_create_purchase_order_invalid_delivery_date(self, client, po_body, bad_date):
        """Test that only real YYYY-MM-DD dates are accepted."""
        response = client.post(
            "/api/purchase-orders", json={**po_body, "expected_delivery_date": bad_date}
        )
        assert response.status_code == 422

    @pytest.mark.parametrize("past_date", [days_from_today(-1), "2020-01-01"])
    def test_create_purchase_order_past_delivery_date(self, client, po_body, past_date):
        """Test that delivery dates before today are rejected with a clear message."""
        response = client.post(
            "/api/purchase-orders", json={**po_body, "expected_delivery_date": past_date}
        )
        assert response.status_code == 422
        assert "today or later" in str(response.json()["detail"])
        assert app.data.purchase_orders == []

    @pytest.mark.parametrize("good_date", [days_from_today(0), days_from_today(365), next_leap_day()])
    def test_create_purchase_order_valid_delivery_date(self, client, po_body, good_date):
        """Test that today, future dates and a leap day are accepted and round-trip unchanged."""
        response = client.post(
            "/api/purchase-orders", json={**po_body, "expected_delivery_date": good_date}
        )
        assert response.status_code == 201
        assert response.json()["expected_delivery_date"] == good_date

    def test_get_purchase_orders_by_backlog_item(self, client, po_body):
        """Test getting the POs for a backlog item."""
        created = client.post("/api/purchase-orders", json=po_body).json()

        response = client.get("/api/purchase-orders/2")
        assert response.status_code == 200
        assert response.json() == [created]

    def test_multiple_purchase_orders_per_backlog_item(self, client, po_body):
        """Test that several POs for one item are all returned, oldest first."""
        first = client.post("/api/purchase-orders", json=po_body).json()
        second = client.post("/api/purchase-orders", json={**po_body, "quantity": 5}).json()
        client.post("/api/purchase-orders", json={**po_body, "backlog_item_id": "3"})

        response = client.get("/api/purchase-orders/2")
        assert [po["id"] for po in response.json()] == [first["id"], second["id"]]

    def test_get_purchase_orders_none(self, client):
        """Test that a known backlog item with no POs returns an empty list."""
        response = client.get("/api/purchase-orders/1")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_purchase_orders_unknown_backlog_item(self, client):
        """Test getting POs for a backlog item that doesn't exist."""
        response = client.get("/api/purchase-orders/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_backlog_reflects_purchase_order(self, client, po_body):
        """Test that has_purchase_order flips to true for that backlog item only."""
        client.post("/api/purchase-orders", json=po_body)

        backlog = client.get("/api/backlog").json()
        flagged = {item["id"]: item["has_purchase_order"] for item in backlog}
        assert flagged["2"] is True
        assert not any(value for item_id, value in flagged.items() if item_id != "2")
