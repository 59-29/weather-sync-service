from unittest.mock import patch
from django.urls import resolve

def test_sync_endpoint_starts_task(client):
    with patch("weather.views.sync_weather.delay") as mocked_delay:
        mocked_delay.return_value.id = "abc123"

        resp = client.post("/api/sync/")
        assert resp.status_code == 202
        data = resp.json()
        assert data["task_id"] == "abc123"
        assert data["status"] == "started"
