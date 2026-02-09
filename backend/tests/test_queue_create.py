"""Tests for queue task creation error handling."""

from types import SimpleNamespace

from deepflow_backend.deps import get_queue_manager
from deepflow_backend.main import app
from deepflow_backend.api import queue as queue_api


class FakeQueueManager:
    """Queue manager stub for create-task tests."""

    def __init__(self):
        self.added = []

    def add_task(self, user_id: str, task_id: str, score: float) -> None:
        self.added.append((user_id, task_id, score))


class FakeInsertQuery:
    """Supabase insert query stub."""

    def __init__(self, fail_message: str | None = None):
        self.fail_message = fail_message
        self.insert_payload = None

    def insert(self, payload):
        self.insert_payload = payload
        return self

    def execute(self):
        if self.fail_message:
            raise RuntimeError(self.fail_message)
        return SimpleNamespace(data=[self.insert_payload])


class FakeSupabaseClient:
    """Supabase client stub scoped to the tasks table."""

    def __init__(self, fail_message: str | None = None):
        self.query = FakeInsertQuery(fail_message=fail_message)

    def table(self, table_name: str):
        assert table_name == "tasks"
        return self.query


class TestQueueCreate:
    """Behavior tests for POST /api/v1/queue."""

    def _post_create(self, client):
        return client.post(
            "/api/v1/queue",
            headers={"Authorization": "Bearer dev-user-11111111-1111-1111-1111-111111111111"},
            json={"title": "Test quick add", "urgency": 5},
        )

    def test_create_task_success_enqueues_task(self, client, monkeypatch):
        fake_queue = FakeQueueManager()
        fake_supabase = FakeSupabaseClient()
        app.dependency_overrides[get_queue_manager] = lambda: fake_queue
        monkeypatch.setattr(queue_api, "get_supabase_admin_client", lambda: fake_supabase)

        try:
            response = self._post_create(client)
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 201
        payload = response.json()
        assert payload["title"] == "Test quick add"
        assert len(fake_queue.added) == 1
        assert fake_queue.added[0][1] == payload["id"]
        assert fake_supabase.query.insert_payload["user_id"] == "11111111-1111-1111-1111-111111111111"

    def test_create_task_db_failure_does_not_enqueue_task(self, client, monkeypatch):
        fake_queue = FakeQueueManager()
        fake_supabase = FakeSupabaseClient(fail_message="insert failed")
        app.dependency_overrides[get_queue_manager] = lambda: fake_queue
        monkeypatch.setattr(queue_api, "get_supabase_admin_client", lambda: fake_supabase)

        try:
            response = self._post_create(client)
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 500
        assert response.json()["detail"] == "Database operation failed while creating task."
        assert fake_queue.added == []

    def test_create_task_reports_service_role_config_error(self, client, monkeypatch):
        fake_queue = FakeQueueManager()
        app.dependency_overrides[get_queue_manager] = lambda: fake_queue

        def raise_config_error():
            raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY is not configured")

        monkeypatch.setattr(queue_api, "get_supabase_admin_client", raise_config_error)

        try:
            response = self._post_create(client)
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 500
        assert (
            response.json()["detail"]
            == "Backend configuration error: SUPABASE_SERVICE_ROLE_KEY is not configured."
        )
        assert fake_queue.added == []
