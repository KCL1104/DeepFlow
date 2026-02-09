"""Tests for development-token authentication behavior."""


class TestDevTokenAuth:
    """Validate dev token parsing and format enforcement."""

    def test_dev_token_with_uuid_is_accepted(self, client):
        token = "dev-user-11111111-1111-1111-1111-111111111111"
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "11111111-1111-1111-1111-111111111111"

    def test_dev_token_with_non_uuid_is_rejected(self, client):
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer dev-user-123"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid development token user id format"
