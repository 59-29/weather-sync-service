import logging
from datetime import datetime, timezone as dt_timezone

import requests
from celery import group, shared_task
from django.utils import timezone

from .models import CityWeather

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

CITIES = [
    {"city_name": "Paris", "latitude": 48.8566, "longitude": 2.3522},
    {"city_name": "London", "latitude": 51.5074, "longitude": -0.1278},
    {"city_name": "New York", "latitude": 40.7128, "longitude": -74.0060},
    {"city_name": "Tokyo", "latitude": 35.6762, "longitude": 139.6503},
]


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


@shared_task(
    bind=True,
    autoretry_for=(requests.RequestException,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def sync_city_weather(self, city: dict):
    city_name = city["city_name"]
    logger.info("Weather sync start city=%s", city_name)

    resp = requests.get(
        OPEN_METEO_URL,
        params={
            "latitude": city["latitude"],
            "longitude": city["longitude"],
            "current_weather": "true",
        },
        timeout=10,
    )
    resp.raise_for_status()

    payload = resp.json()
    cw = payload.get("current_weather") or {}

    CityWeather.objects.update_or_create(
        city_name=city_name,
        defaults={
            "latitude": city["latitude"],
            "longitude": city["longitude"],
            "temperature": cw.get("temperature"),
            "windspeed": cw.get("windspeed"),
            "winddirection": cw.get("winddirection"),
            "weathercode": cw.get("weathercode"),
            "weather_time": parse_iso_datetime(cw.get("time")),
            "raw_payload": payload,
            "synced_at": timezone.now(),
        },
    )

    logger.info(
        "Weather sync done city=%s temp=%s windspeed=%s code=%s",
        city_name,
        cw.get("temperature"),
        cw.get("windspeed"),
        cw.get("weathercode"),
    )
    return {"city": city_name, "ok": True}


@shared_task
def sync_all_weather():
    logger.info("Weather sync all queued count=%d", len(CITIES))
    job = group(sync_city_weather.s(city) for city in CITIES)
    result = job.apply_async()
    logger.info("Weather sync all started group_id=%s", result.id)
    return {"group_id": result.id}
