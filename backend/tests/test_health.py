"""Tests for health endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_application


@pytest.fixture
def client() -> TestClient:
    """Create a test client with a fresh application instance."""
    app = create_application()
    with TestClient(app) as c:
        yield c


def test_root(client: TestClient) -> None:
    """Root endpoint returns service identification."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Astra-Invest"
    assert data["status"] == "running"
    assert "version" in data


def test_health(client: TestClient) -> None:
    """Liveness endpoint returns ok."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data


def test_ready(client: TestClient) -> None:
    """Readiness endpoint returns a structured response.

    Without a live Postgres the database check will be 'error: ...',
    so overall status may be 'degraded'. That is expected in unit tests.
    """
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in {"ok", "degraded"}
    assert "application" in data["checks"]
