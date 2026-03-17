from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    with open("app/dashboard.html", "r") as f:
        return f.read()