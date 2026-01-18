"""
Pytest Configuration and Fixtures

Provides test fixtures for API testing.
"""

import pytest
from fastapi.testclient import TestClient

# Mock environment variables before importing app
import os
os.environ.setdefault("SUPABASE_URL", "https://mock.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "mock-anon-key")
os.environ.setdefault("UPSTASH_REDIS_URL", "redis://localhost:6379")

from deepflow_backend.main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Mock authenticated user."""
    return {
        "id": "test-user-123",
        "email": "test@example.com",
    }


@pytest.fixture
def sample_task():
    """Sample task data for testing."""
    return {
        "title": "Test Task",
        "summary": "This is a test task",
        "urgency": 5,
        "estimated_minutes": 30,
    }
