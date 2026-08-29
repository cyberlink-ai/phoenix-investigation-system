"""
Phoenix backend entry point.

Run locally:
    cd backend
    pip install -r requirements.txt
    uvicorn app.main:app --reload --port 8000

Deployment note (see root README.md): this backend needs a host with
persistent, long-running compute (Render, Railway, Fly.io, or similar).
Vercel's serverless functions are not suitable once real YOLO/OpenCV
processing is wired in (execution-time limits, no GPU, large package sizes).
The React frontend is what goes on Vercel; this API is deployed separately
and the frontend simply points at its URL.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import cameras, evidence, investigations, vehicles, videos
from app.core.config import settings
from app.db.supabase_client import is_db_connected

app = FastAPI(
    title="Phoenix API",
    description="Autonomous Investigation Decision-Support System — backend for SIH26127",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cameras.router)
app.include_router(vehicles.router)
app.include_router(investigations.router)
app.include_router(evidence.router)
app.include_router(videos.router)


@app.get("/")
def root():
    return {"service": "phoenix-backend", "status": "ok"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "env": settings.ENV,
        "database_connected": is_db_connected(),
        "note": "database_connected will be false until Supabase credentials are set (Phase: Database)",
    }
