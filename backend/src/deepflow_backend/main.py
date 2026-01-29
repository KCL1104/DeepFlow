"""
DeepFlow Backend - FastAPI Application

Main entry point for the API server.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .api import state_router, queue_router, tasks_router, pomodoro_router, auth_router, notifications_router, webhooks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    settings = get_settings()
    print(f"🚀 DeepFlow Backend starting in {settings.app_env} mode")
    yield
    # Shutdown
    print("👋 DeepFlow Backend shutting down")


app = FastAPI(
    title="DeepFlow API",
    description="Intelligent task scheduling and focus protection API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(state_router, prefix="/api/v1")
app.include_router(queue_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(pomodoro_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(webhooks_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "deepflow-backend"}


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "version": "0.1.0",
    }
