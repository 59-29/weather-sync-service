from unittest.mock import patch

from weather.models import CityWeather
from weather.tasks import sync_city_weather

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
    def raise_for_status(self):
        return None

    def json(self):
        return FAKE_PAYLOAD


CITIES = [
    {"city_name": "Paris", "latitude": 48.8566, "longitude": 2.3522},
    {"city_name": "London", "latitude": 51.5074, "longitude": -0.1278},
    {"city_name": "New York", "latitude": 40.7128, "longitude": -74.0060},
    {"city_name": "Tokyo", "latitude": 35.6762, "longitude": 139.6503},
]


@patch("weather.tasks.requests.get", return_value=FakeResp())
def test_sync_task_upserts(mock_get, db):
    for city in CITIES:
        result = sync_city_weather(city)
        assert result["ok"] is True

    assert CityWeather.objects.count() == 4

    paris = CityWeather.objects.get(city_name="Paris")
    assert paris.temperature == 10.5
    assert paris.raw_payload is not None
    assert paris.synced_at is not None

    for city in CITIES:
        sync_city_weather(city)

    assert CityWeather.objects.count() == 4
