"""
health.py — Health Check Endpoint
===================================
Provides /health and /ready endpoints for:
  - AWS Load Balancer health checks
  - Docker HEALTHCHECK instruction
  - Uptime monitoring services (UptimeRobot, etc.)

Returns JSON with app status, version, uptime, and environment.
Uses FastAPI APIRouter so routes can be included in Gradio's app.
"""

import time
import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from config import APP_VERSION, APP_ENV, GROQ_API_KEY, TAVILY_API_KEY

logger = logging.getLogger(__name__)

# Track when the app started
_start_time = time.time()

# Create a router (not a full FastAPI app) so it can be included
# in Gradio's internal FastAPI app via app.include_router()
health_router = APIRouter(tags=["Health"])


@health_router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        JSON with status, version, uptime, and environment info.

    Used by:
        - Docker HEALTHCHECK
        - AWS ALB/NLB target group health checks
        - Monitoring tools
    """
    uptime_seconds = round(time.time() - _start_time, 1)

    # Check if required API keys are configured
    checks = {
        "groq_api_key": bool(GROQ_API_KEY),
        "tavily_api_key": bool(TAVILY_API_KEY),
    }

    # Overall status: healthy only if all keys are set
    all_healthy = all(checks.values())

    response = {
        "status": "healthy" if all_healthy else "degraded",
        "version": APP_VERSION,
        "environment": APP_ENV,
        "uptime_seconds": uptime_seconds,
        "checks": checks,
    }

    status_code = 200 if all_healthy else 503
    logger.debug("Health check: %s (status=%d)", response["status"], status_code)

    return JSONResponse(content=response, status_code=status_code)


@health_router.get("/ready")
async def readiness_check():
    """
    Readiness probe — returns 200 only when the app is fully ready.
    Useful for Kubernetes readiness probes or ECS health checks.
    """
    if GROQ_API_KEY:
        return JSONResponse(content={"ready": True}, status_code=200)

    return JSONResponse(
        content={"ready": False, "reason": "GROQ_API_KEY not configured"},
        status_code=503,
    )
