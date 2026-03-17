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
        name="google",
        url="https://www.google.com",
        warn_latency_ms=800,
        crit_latency_ms=2000,
    ),
    ServiceConfig(
        name="github",
        url="https://github.com",
        warn_latency_ms=800,
        crit_latency_ms=2000,
    ),
    ServiceConfig(
        name="httpbin",
        url="https://httpbin.org/get",
        warn_latency_ms=2000,
        crit_latency_ms=5000,
    ),
]

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL", "")
DB_PATH       = os.getenv("DB_PATH", "health.db")

