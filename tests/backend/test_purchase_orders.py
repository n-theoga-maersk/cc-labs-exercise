"""
Tests for purchase order API endpoints (SPEC-0001).
"""
import json
from datetime import date, timedelta

import pytest

import app.data


def days_from_today(days):
    """ISO date relative to today. Call inside the test, not at collection, so a run that
    crosses midnight still computes "today" correctly."""
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


def expected_id(baseline, n=1):
    """ID of the n-th PO created in this test, given the POs that existed before it."""
    return f"PO-{len(baseline) + n:04d}"


@pytest.fixture(autouse=True)
def baseline():
    """POs live in a module-level list shared by every test; restore it in place after each test.

    Yields a copy of the POs that existed before the test, so assertions don't assume an
    empty store. Slice assignment keeps the same list object, which the routers hold by reference.
    """
    saved = list(app.data.purchase_orders)
    yield saved
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

    def test_create_purchase_order(self, client, po_body, baseline):
        """Test creating a purchase order sets server fields and echoes the body."""
        response = client.post("/api/purchase-orders", json=po_body)
        assert response.status_code == 201

        po = response.json()
        for field, value in po_body.items():
            assert po[field] == value
        assert po["id"] == expected_id(baseline)
        assert po["status"] == "Pending"
        assert "T" in po["created_date"]

    def test_create_purchase_order_ids_are_sequential(self, client, po_body, baseline):
        """Test that IDs follow the PO-NNNN sequence."""
        first = client.post("/api/purchase-orders", json=po_body).json()
        second = client.post("/api/purchase-orders", json=po_body).json()
        assert (first["id"], second["id"]) == (expected_id(baseline, 1), expected_id(baseline, 2))

    def test_create_purchase_order_ignores_client_status(self, client, po_body, baseline):
        """Test that the client cannot choose the initial status or id."""
        response = client.post(
            "/api/purchase-orders", json={**po_body, "status": "Approved", "id": "HACK"}
        )
        assert response.status_code == 201
        assert response.json()["status"] == "Pending"
        assert response.json()["id"] == expected_id(baseline)

    def test_create_purchase_order_unknown_backlog_item(self, client, po_body, baseline):
        """Test creating a PO for a backlog item that doesn't exist."""
        response = client.post(
            "/api/purchase-orders", json={**po_body, "backlog_item_id": "999"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
        assert app.data.purchase_orders == baseline

    @pytest.mark.parametrize("override", [
        {"quantity": 0},
        {"quantity": -5},
        {"unit_cost": -1},
        {"supplier_name": ""},
        {"supplier_name": "   "},
    ])
    def test_create_purchase_order_invalid_body(self, client, po_body, baseline, override):
        """Test that invalid field values are rejected."""
        response = client.post("/api/purchase-orders", json={**po_body, **override})
        assert response.status_code == 422
        assert app.data.purchase_orders == baseline

    @pytest.mark.parametrize("raw_cost", ["NaN", "Infinity", "-Infinity"])
    def test_create_purchase_order_non_finite_unit_cost(self, client, po_body, baseline, raw_cost):
        """Test that NaN/Infinity get a JSON 422, not a 500 or a stored null.

        Python's json module accepts these non-standard literals, so send the body raw.
        """
        raw = json.dumps({**po_body, "unit_cost": 0}).replace('"unit_cost": 0', f'"unit_cost": {raw_cost}')
        response = client.post(
            "/api/purchase-orders", content=raw, headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
        assert response.json()["detail"][0]["loc"] == ["body", "unit_cost"]
        assert app.data.purchase_orders == baseline

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

    @pytest.mark.parametrize("past", ["yesterday", "2020-01-01"])
    def test_create_purchase_order_past_delivery_date(self, client, po_body, baseline, past):
        """Test that delivery dates before today are rejected with a clear message."""
        past_date = days_from_today(-1) if past == "yesterday" else past
        response = client.post(
            "/api/purchase-orders", json={**po_body, "expected_delivery_date": past_date}
        )
        assert response.status_code == 422
        assert "today or later" in str(response.json()["detail"])
        assert app.data.purchase_orders == baseline

    @pytest.mark.parametrize("when", ["today", "in_a_year", "next_leap_day"])
    def test_create_purchase_order_valid_delivery_date(self, client, po_body, when):
        """Test that today, future dates and a leap day are accepted and round-trip unchanged."""
        good_date = {
            "today": lambda: days_from_today(0),
            "in_a_year": lambda: days_from_today(365),
            "next_leap_day": next_leap_day,
        }[when]()
        response = client.post(
            "/api/purchase-orders", json={**po_body, "expected_delivery_date": good_date}
        )
        assert response.status_code == 201
        assert response.json()["expected_delivery_date"] == good_date

    def test_get_purchase_orders_by_backlog_item(self, client, po_body, baseline):
        """Test getting the POs for a backlog item."""
        existing = [po for po in baseline if po["backlog_item_id"] == "2"]
        created = client.post("/api/purchase-orders", json=po_body).json()

        response = client.get("/api/purchase-orders/2")
        assert response.status_code == 200
        assert response.json() == existing + [created]

    def test_multiple_purchase_orders_per_backlog_item(self, client, po_body, baseline):
        """Test that several POs for one item are all returned, oldest first."""
        existing_ids = [po["id"] for po in baseline if po["backlog_item_id"] == "2"]
        first = client.post("/api/purchase-orders", json=po_body).json()
        second = client.post("/api/purchase-orders", json={**po_body, "quantity": 5}).json()
        client.post("/api/purchase-orders", json={**po_body, "backlog_item_id": "3"})

        response = client.get("/api/purchase-orders/2")
        assert [po["id"] for po in response.json()] == existing_ids + [first["id"], second["id"]]

    def test_get_purchase_orders_none(self, client, baseline):
        """Test that a known backlog item with no POs returns an empty list."""
        item_ids = {item["id"] for item in app.data.backlog_items}
        without_po = sorted(item_ids - {po["backlog_item_id"] for po in baseline})
        assert without_po, "test needs at least one backlog item without a PO"

        response = client.get(f"/api/purchase-orders/{without_po[0]}")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_purchase_orders_unknown_backlog_item(self, client):
        """Test getting POs for a backlog item that doesn't exist."""
        response = client.get("/api/purchase-orders/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_backlog_reflects_purchase_order(self, client, po_body, baseline):
        """Test that has_purchase_order flips to true for that item and nothing else changes."""
        before = {item["id"]: item["has_purchase_order"] for item in client.get("/api/backlog").json()}
        if not any(po["backlog_item_id"] == "2" for po in baseline):
            assert before["2"] is False
        client.post("/api/purchase-orders", json=po_body)
        after = {item["id"]: item["has_purchase_order"] for item in client.get("/api/backlog").json()}

        assert after["2"] is True
        assert {k: v for k, v in after.items() if k != "2"} == {k: v for k, v in before.items() if k != "2"}
