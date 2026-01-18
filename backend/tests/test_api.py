"""
Tests for API Endpoints

Tests the FastAPI routes using TestClient.
"""

import pytest


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns ok status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "deepflow-backend"

    def test_health_endpoint(self, client):
        """Test health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestStateAPI:
    """Test state API endpoints."""

    def test_get_state_requires_auth(self, client):
        """Test that state endpoint requires authentication."""
        response = client.get("/api/v1/state")
        assert response.status_code == 401

    def test_get_state_with_invalid_token(self, client):
        """Test that invalid token is rejected."""
        response = client.get(
            "/api/v1/state",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401


class TestQueueAPI:
    """Test queue API endpoints."""

    def test_get_queue_requires_auth(self, client):
        """Test that queue endpoint requires authentication."""
        response = client.get("/api/v1/queue")
        assert response.status_code == 401

    def test_create_task_requires_auth(self, client, sample_task):
        """Test that task creation requires authentication."""
        response = client.post("/api/v1/queue", json=sample_task)
        assert response.status_code == 401


class TestPomodoroAPI:
    """Test pomodoro API endpoints."""

    def test_get_pomodoro_requires_auth(self, client):
        """Test that pomodoro settings endpoint requires authentication."""
        response = client.get("/api/v1/pomodoro/settings")
        assert response.status_code == 401


class TestAuthAPI:
    """Test auth API endpoints."""

    def test_get_me_requires_auth(self, client):
        """Test that /auth/me requires authentication."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
