from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.store import init_db
from app.checker import start_scheduler
from app.api import app as api_app

scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler
    await init_db()
    scheduler = start_scheduler()
    print("Health monitor started — polling services...")
    yield
    scheduler.shutdown()
    print("Health monitor stopped.")

app = FastAPI(lifespan=lifespan)
app.mount("/", api_app)