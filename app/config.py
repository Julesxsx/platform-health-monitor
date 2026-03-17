from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class ServiceConfig(BaseModel):
    name: str
    url: str
    interval_seconds: int = 30
    timeout_seconds: int = 5
    sla_uptime_pct: float = 99.0
    warn_latency_ms: int = 300
    crit_latency_ms: int = 1000
    expected_status: int = 200

SERVICES: List[ServiceConfig] = [
    ServiceConfig(
        name="api-gateway",
        url="http://localhost:8001/health",
        warn_latency_ms=500,
        crit_latency_ms=1000,
    ),
    ServiceConfig(
        name="worker-service",
        url="http://localhost:8002/health",
        warn_latency_ms=500,
        crit_latency_ms=1000,
        expected_status=200,
    ),
    ServiceConfig(
        name="flaky-queue",
        url="http://localhost:8003/health",
        warn_latency_ms=500,
        crit_latency_ms=1200,
    ),
]

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL", "")
DB_PATH       = os.getenv("DB_PATH", "health.db")

