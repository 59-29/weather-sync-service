from celery import shared_task
from django.utils import timezone
from datetime import datetime, timezone as dt_timezone
import requests

from .models import CityWeather

CITIES = [
    {"city_name": "Paris", "latitude": 48.8566, "longitude": 2.3522},
    {"city_name": "London", "latitude": 51.5074, "longitude": -0.1278},
    {"city_name": "New York", "latitude": 40.7128, "longitude": -74.0060},
    {"city_name": "Tokyo", "latitude": 35.6762, "longitude": 139.6503},
]

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

def parse_iso_datetime(value: str):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=dt_timezone.utc)
        return dt
    except ValueError:
        return None

@shared_task
def sync_weather():
    results = {"updated": 0, "failed": 0}

    for c in CITIES:
        try:
            resp = requests.get(
                OPEN_METEO_URL,
                params={
                    "latitude": c["latitude"],
                    "longitude": c["longitude"],
                    "current_weather": "true",
                },
                timeout=10,
            )
            resp.raise_for_status()
            payload = resp.json()
            cw = payload.get("current_weather") or {}

            CityWeather.objects.update_or_create(
                city_name=c["city_name"],
                defaults={
                    "latitude": c["latitude"],
                    "longitude": c["longitude"],
                    "temperature": cw.get("temperature"),
                    "windspeed": cw.get("windspeed"),
                    "winddirection": cw.get("winddirection"),
                    "weathercode": cw.get("weathercode"),
                    "weather_time": parse_iso_datetime(cw.get("time")),
                    "raw_payload": payload,
                    "synced_at": timezone.now(),
                },
            )
            results["updated"] += 1

        except requests.RequestException:
            results["failed"] += 1
            continue

    return results
