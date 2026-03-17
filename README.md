# Platform Health Monitor

Automated Python service that monitors platform uptime, tracks SLA 
compliance, and fires alerts on degradation or downtime.

## Features
- Polls services every 30s and records latency + HTTP status
- Fires alerts on state changes — UP / DEGRADED / DOWN
- REST API exposes /health, /metrics, /incidents
- Live dashboard with latency charts, SLA bars, incident log
- Fully containerized with Docker

## Tech stack
- FastAPI, APScheduler, SQLAlchemy, SQLite, Docker

## Run locally
git clone https://github.com/Julesxsx/platform-health-monitor
cd platform-health-monitor
cp .env.example .env
docker compose -f docker/docker-compose.yml up --build

## Access
Once running, open your browser and go to:

| URL | Description |
|---|---|
| http://localhost:8000/dashboard | Live dashboard |
| http://localhost:8000/health | JSON health summary |
| http://localhost:8000/metrics/{service} | Per-service metrics |
| http://localhost:8000/incidents | Incident log |
| http://localhost:8000/docs | Interactive API docs |

## Test services
Three simulated services are included to demonstrate the monitor in action:
- **api-gateway** (port 8001) — always healthy, stable latency
- **worker-service** (port 8002) — goes DOWN every 5th request
- **flaky-queue** (port 8003) — random latency spikes simulating degradation





