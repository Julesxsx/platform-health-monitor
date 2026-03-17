from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, desc
from app.store import uptime_pct, get_recent_checks, get_incidents, CheckResult, AsyncSession, engine
from app.config import SERVICES

app = FastAPI(title="Platform Health Monitor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_summary():
    results = []
    for svc in SERVICES:
        pct = await uptime_pct(svc.name, hours=24)
        async with AsyncSession(engine) as s:
            row = await s.scalar(
                select(CheckResult)
                .where(CheckResult.service == svc.name)
                .order_by(desc(CheckResult.ts))
                .limit(1)
            )
        results.append({
            "service":      svc.name,
            "status":       "up" if row and row.up else "down",
            "latency_ms":   row.latency_ms if row else None,
            "uptime_24h":   pct,
            "sla_target":   svc.sla_uptime_pct,
            "sla_ok":       pct >= svc.sla_uptime_pct,
            "last_checked": row.ts.isoformat() if row else None,
            "error":        row.error if row else None,
        })
    return {
        "services":     results,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/metrics/{service}")
async def service_metrics(service: str, hours: int = 24):
    names = [s.name for s in SERVICES]
    if service not in names:
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")

    rows = await get_recent_checks(service, limit=200)
    latencies = sorted([r.latency_ms for r in rows if r.latency_ms])
    p95 = latencies[int(len(latencies) * 0.95) - 1] if latencies else None

    return {
        "service":        service,
        "hours":          hours,
        "total_checks":   len(rows),
        "uptime_pct":     await uptime_pct(service, hours),
        "avg_latency_ms": round(sum(latencies) / len(latencies)) if latencies else None,
        "p95_latency_ms": p95,
        "timeline": [
            {"ts": r.ts.isoformat(), "up": r.up, "latency_ms": r.latency_ms}
            for r in rows
        ],
    }

@app.get("/incidents")
async def incidents(hours: int = 24):
    rows = await get_incidents(hours=hours)
    return {
        "incidents": [
            {
                "service":    r.service,
                "ts":         r.ts.isoformat(),
                "status":     r.status,
                "latency_ms": r.latency_ms,
                "error":      r.error,
            }
            for r in rows
        ],
        "total": len(rows),
    }

@app.get("/services")
async def list_services():
    return {
        "services": [
            {
                "name":             s.name,
                "url":              s.url,
                "interval_seconds": s.interval_seconds,
                "sla_uptime_pct":   s.sla_uptime_pct,
                "warn_latency_ms":  s.warn_latency_ms,
                "crit_latency_ms":  s.crit_latency_ms,
            }
            for s in SERVICES
        ]
    }