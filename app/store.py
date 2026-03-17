from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import String, Float, Boolean, DateTime, select, func, desc
from datetime import datetime, timezone, timedelta
from app.config import DB_PATH

engine = create_async_engine(f"sqlite+aiosqlite:///{DB_PATH}")

class Base(DeclarativeBase):
    pass

class CheckResult(Base):
    __tablename__ = "checks"
    id:         Mapped[int]        = mapped_column(primary_key=True, autoincrement=True)
    service:    Mapped[str]        = mapped_column(String(80), index=True)
    ts:         Mapped[datetime]   = mapped_column(DateTime(timezone=True))
    status:     Mapped[int|None]   = mapped_column(nullable=True)
    latency_ms: Mapped[float|None] = mapped_column(nullable=True)
    up:         Mapped[bool]       = mapped_column(Boolean, default=False)
    error:      Mapped[str|None]   = mapped_column(String(200), nullable=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def write_check(data: dict):
    async with AsyncSession(engine) as s:
        s.add(CheckResult(**data))
        await s.commit()

async def uptime_pct(service: str, hours: int = 24) -> float:
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    async with AsyncSession(engine) as s:
        total = await s.scalar(
            select(func.count()).where(
                CheckResult.service == service,
                CheckResult.ts >= since
            )
        )
        up = await s.scalar(
            select(func.count()).where(
                CheckResult.service == service,
                CheckResult.ts >= since,
                CheckResult.up == True
            )
        )
        return round((up / total * 100) if total else 0.0, 3)

async def get_recent_checks(service: str, limit: int = 100):
    async with AsyncSession(engine) as s:
        rows = (await s.scalars(
            select(CheckResult)
            .where(CheckResult.service == service)
            .order_by(desc(CheckResult.ts))
            .limit(limit)
        )).all()
        return rows

async def get_incidents(hours: int = 24):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    async with AsyncSession(engine) as s:
        rows = (await s.scalars(
            select(CheckResult)
            .where(
                CheckResult.ts >= since,
                CheckResult.up == False
            )
            .order_by(desc(CheckResult.ts))
        )).all()
        return rows