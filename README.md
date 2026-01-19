# Weather Sync Service

## Overview
This project is a backend service that synchronizes current weather data from the Open-Meteo API for a predefined list of cities using a Celery background task, and exposes the data through REST APIs built with Django REST Framework.

The weather synchronization runs asynchronously and returns immediately when triggered.

**Cities synced:**
- Paris
- London
- New York
- Tokyo

---

## Tech Stack
- Python
- Django
- Django REST Framework
- PostgreSQL
- Celery
- Redis
- Docker / docker-compose (for infrastructure)

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/59-29/weather-sync-service.git
cd weather-sync-service
````

---

### 2. Create virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 3. Environment variables (Required)

```bash
export DJANGO_SECRET_KEY="change-me"
export DEBUG="1"

export POSTGRES_DB="weatherdb"
export POSTGRES_USER="weatheruser"
export POSTGRES_PASSWORD="weatherpass"
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5432"

export CELERY_BROKER_URL="redis://localhost:6379/0"
export CELERY_RESULT_BACKEND="redis://localhost:6379/0"

export CORS_ALLOWED_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"
export CSRF_TRUSTED_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"

export PAGE_SIZE="10"
```

---

### 4. Start PostgreSQL and Redis

Using docker-compose:

```bash
podman-compose up -d
```
---

### 5. Run database migrations

```bash
python manage.py migrate
```

---

## Run the Application

### Terminal 1 — Start Django server

```bash
python manage.py runserver
```

---

### Terminal 2 — Start Celery worker

```bash
celery -A config worker -l info
```

---

## API Endpoints

### POST `/api/sync/`

Triggers the background weather sync task.

**Example:**

```json
{"task_id":"uuid","status":"started"}
```

The request returns immediately.

---

### GET `/api/weather/`

Returns the latest weather data for all cities.

**Example:**

```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [...]
}
```

---

### GET `/api/weather/<id>/`

Returns weather data for a single city.

---

## Tests

Run unit tests with:

```bash
pytest -q
```

---

## Features 

* Each city has exactly one database record without duplicates.
* Re-syncing updates existing records.
* Celery tasks per city for concurrency.
* Database indexes for better/efficient lookups
* If a single city fails during sync, the other cities will continue.
* The full Open-Meteo response is stored for debugging.
* CORS and CRSF configuration.

---

## Scaling

For syncing thousands of cities every hour, I would:
* Storing the cities in a database instead of hardcoding them in the code
* Use a scheduler like to run sync jobs automatically
* Split the work into smaller background tasks instead of one large task
* Add rate limiting and retries to handle API failures
* Use logging and monitoring to observe failures and performance

---


