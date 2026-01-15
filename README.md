# Weather Sync Service (Django + Celery)

## Overview
Small backend service that syncs current weather data from Open-Meteo for a predefined list of cities using a Celery background job, and exposes results via REST APIs.

Cities: Paris, London, New York, Tokyo.

## Tech Stack
- Python + Django + DRF
- Postgres
- Celery
- Redis (broker/backend)

## Setup

### 1) Create venv and install deps
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
