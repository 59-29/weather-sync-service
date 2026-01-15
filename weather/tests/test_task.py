from unittest.mock import patch
from weather.models import CityWeather
from weather.tasks import sync_weather

FAKE_PAYLOAD = {
    "current_weather": {
        "temperature": 10.5,
        "windspeed": 3.2,
        "winddirection": 180,
        "weathercode": 2,
        "time": "2026-01-15T10:00",
    }
}

class FakeResp:
    def raise_for_status(self):  # no error
        return None
    def json(self):
        return FAKE_PAYLOAD

@patch("weather.tasks.requests.get", return_value=FakeResp())
def test_sync_task_upserts(mock_get, db):

    result = sync_weather()

    assert CityWeather.objects.count() == 4
    paris = CityWeather.objects.get(city_name="Paris")
    assert paris.temperature == 10.5
    assert paris.raw_payload is not None
    assert paris.synced_at is not None

    sync_weather()
    assert CityWeather.objects.count() == 4

    assert result["updated"] == 4
