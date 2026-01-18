"""
Opik Tracer Module

Provides tracing and observability for Agent calls.
"""

from functools import wraps
from typing import Callable, Any, Optional
import os

# Try to import opik, handle gracefully if not configured
try:
    import opik
    from opik import track

    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    track = None

from .config import get_settings


def init_opik() -> bool:
    """Initialize Opik with project settings. Returns True if successful."""
    if not OPIK_AVAILABLE:
        print("⚠️ Opik not installed")
        return False

    settings = get_settings()

    if not settings.opik_api_key:
        print("⚠️ Opik API key not configured")
        return False

    try:
        opik.configure(
            api_key=settings.opik_api_key,
            workspace=settings.opik_workspace,
        )
        print(f"✅ Opik initialized: project={settings.opik_project_name}")
        return True
    except Exception as e:
        print(f"❌ Opik initialization failed: {e}")
        return False


def trace_agent(name: str):
    """
    Decorator to trace agent function calls with Opik.
    Falls back gracefully if Opik is not available.
    """
    def decorator(func: Callable) -> Callable:
        if OPIK_AVAILABLE and track:
            @track(name=name)
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            @track(name=name)
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            # Return appropriate wrapper based on function type
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper
        else:
            return func

    return decorator


class OpikTracer:
    """
    Context manager for tracing spans within Opik.
    """

    def __init__(self, name: str, metadata: Optional[dict] = None):
        self.name = name
        self.metadata = metadata or {}
        self.trace = None

    def __enter__(self):
        if OPIK_AVAILABLE:
            settings = get_settings()
            try:
                self.trace = opik.Trace(
                    name=self.name,
                    project_name=settings.opik_project_name,
                    metadata=self.metadata,
                )
            except Exception:
                pass
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.trace:
            try:
                self.trace.end()
            except Exception:
                pass
        return False

    def log(self, key: str, value: Any):
        """Log a key-value pair to the current trace."""
        if self.trace:
            try:
                self.trace.log_metadata({key: value})
            except Exception:
                pass
