import httpx
from datetime import datetime, timezone, timedelta
from app.config import ServiceConfig, SLACK_WEBHOOK

_last_state: dict[str, str] = {}
_last_alert: dict[str, datetime] = {}
COOLDOWN_MINUTES = 10

def compute_state(svc: ServiceConfig, result: dict) -> str:
    if not result["up"]:
        return "DOWN"
    lat = result.get("latency_ms") or 0
    if lat >= svc.crit_latency_ms:
        return "DOWN"
    if lat >= svc.warn_latency_ms:
        return "DEGRADED"
    return "UP"

async def evaluate(svc: ServiceConfig, result: dict):
    new_state = compute_state(svc, result)
    prev_state = _last_state.get(svc.name, "UP")
    last_alerted = _last_alert.get(svc.name)
    now = datetime.now(timezone.utc)

    state_changed = new_state != prev_state
    cooled_down = not last_alerted or \
        (now - last_alerted) > timedelta(minutes=COOLDOWN_MINUTES)

    if state_changed or (new_state != "UP" and cooled_down):
        _last_state[svc.name] = new_state
        _last_alert[svc.name] = now
        print(f"[ALERT] {svc.name} → {new_state} | latency: {result.get('latency_ms')}ms | error: {result.get('error')}")
        await send_slack(svc.name, new_state, result)

async def send_slack(name: str, state: str, result: dict):
    if not SLACK_WEBHOOK:
        return
    icons = {"UP": ":white_check_mark:", "DEGRADED": ":warning:", "DOWN": ":red_circle:"}
    payload = {"text": (
        f"{icons[state]} *{name}* is *{state}*\n"
        f"Latency: {result.get('latency_ms', '—')}ms  |  "
        f"HTTP: {result.get('status', '—')}  |  "
        f"{result.get('error') or ''}"
    )}
    async with httpx.AsyncClient() as c:
        await c.post(SLACK_WEBHOOK, json=payload, timeout=5)