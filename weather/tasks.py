from celery import shared_task
from django.utils import timezone
from datetime import datetime, timezone as dt_timezone
import requests
import logging
from .models import CityWeather

logger = logging.getLogger(__name__)

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

@shared_task(
    bind=True,
    autoretry_for=(requests.RequestException,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def sync_weather(self):
    results = {"updated": 0, "failed": 0}

    logger.info("Weather sync started for %d cities", len(CITIES))

    for c in CITIES:
        try:
            logger.info("Fetching weather for city=%s", c["city_name"])

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
            logger.info(
                "Synced city=%s temp=%s windspeed=%s",
                c["city_name"],
                cw.get("temperature"),
                cw.get("windspeed"),
            )

        except requests.RequestException as e:
            results["failed"] += 1
            logger.warning(
                "Failed syncing city=%s error=%s",
                c["city_name"],
                str(e),
            )
            raise

    logger.info("Weather sync finished: %s", results)
    return results 
