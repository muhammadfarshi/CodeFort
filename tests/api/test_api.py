"""
Tests for CodeFort FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app_name"] == "CodeFort"


def test_root_health():
    """Test root health endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_demo_scan():
    """Test demo scan execution."""
    response = client.post("/api/webhooks/demo-scan")
    assert response.status_code == 200
    data = response.json()
    assert "scan_id" in data
    assert data["findings_count"] > 0
    assert data["policy_decision"] in ["pass", "review", "block"]


def test_scans_list():
    """Test listing scans endpoint."""
    # Ensure at least one scan exists
    client.post("/api/webhooks/demo-scan")
    response = client.get("/api/scans/")
    assert response.status_code == 200
    scans = response.json()
    assert isinstance(scans, list)
    assert len(scans) > 0


def test_scan_detail_not_found():
    """Test 404 for nonexistent scan."""
    response = client.get("/api/scans/nonexistent-uuid")
    assert response.status_code == 404
