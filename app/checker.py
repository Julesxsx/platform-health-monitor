import httpx
import time
import asyncio
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import SERVICES, ServiceConfig
from app.store import write_check
from app.alerts import evaluate

async def check_service(svc: ServiceConfig):
    start = time.monotonic()
    status, latency_ms, error = None, None, None

    try:
        async with httpx.AsyncClient(timeout=svc.timeout_seconds) as client:
            r = await client.get(svc.url)
            status = r.status_code
            latency_ms = round((time.monotonic() - start) * 1000)
    except httpx.TimeoutException:
        error = "timeout"
    except Exception as e:
        error = str(e)[:120]

    result = dict(
        service=svc.name,
        ts=datetime.now(timezone.utc),
        status=status,
        latency_ms=latency_ms,
        up=status == svc.expected_status if status else False,
        error=error,
    )

    await write_check(result)
    await evaluate(svc, result)
    print(f"[CHECK] {svc.name} | up={result['up']} | latency={result['latency_ms']}ms | status={result['status']}")

def start_scheduler():
    scheduler = AsyncIOScheduler()
    for svc in SERVICES:
        scheduler.add_job(
            check_service,
            "interval",
            seconds=svc.interval_seconds,
            args=[svc],
            id=svc.name,
            next_run_time=datetime.now(timezone.utc),
        )
    scheduler.start()
    return scheduler

