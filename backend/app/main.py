import os
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.config import get_settings
from app.core.database import check_database_health, engine
from app.core.redis import check_redis_health, close_redis, get_redis_client
from app.services.events import generation_event_stream
from app.utils.logging import configure_logging, get_logger
from app.utils.metrics import REQUEST_COUNT, REQUEST_LATENCY, metrics_response

settings = get_settings()
configure_logging()
logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(_: FastAPI):
    os.makedirs("generated_portfolios", exist_ok=True)
    logger.info("startup_complete")
    yield
    await close_redis()
    await engine.dispose()
    logger.info("shutdown_complete")


app = FastAPI(
    title="DevForge API",
    description="AI-powered developer portfolio generator backend",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def telemetry_middleware(request: Request, call_next):
    correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))
    start = time.perf_counter()
    path = request.url.path
    method = request.method
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "request_failed",
            correlation_id=correlation_id,
            method=method,
            path=path,
        )
        REQUEST_COUNT.labels(method=method, path=path, status_code="500").inc()
        raise

    duration = time.perf_counter() - start
    REQUEST_COUNT.labels(method=method, path=path, status_code=str(response.status_code)).inc()
    REQUEST_LATENCY.labels(method=method, path=path).observe(duration)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


@app.get("/health")
async def health() -> JSONResponse:
    db_ok = await check_database_health()
    redis_ok = await check_redis_health()
    status_code = 200 if db_ok and redis_ok else 503
    return JSONResponse(
        status_code=status_code,
        content={"status": "ok" if status_code == 200 else "degraded", "db": db_ok, "redis": redis_ok},
    )


@app.get("/health/ready")
async def ready() -> JSONResponse:
    db_ok = await check_database_health()
    redis_ok = await check_redis_health()
    if db_ok and redis_ok:
        return JSONResponse(status_code=200, content={"ready": True})
    return JSONResponse(status_code=503, content={"ready": False, "db": db_ok, "redis": redis_ok})


@app.get("/metrics")
async def metrics():
    if not settings.enable_metrics:
        return JSONResponse(status_code=404, content={"detail": "Metrics disabled"})
    return metrics_response()


@app.websocket("/ws/generation/{job_id}")
async def generation_ws(websocket: WebSocket, job_id: str):
    await websocket.accept()
    redis = get_redis_client()
    try:
        await websocket.send_json({"event": "connected", "job_id": job_id})
        async for event in generation_event_stream(redis, job_id):
            await websocket.send_json(event)
    except WebSocketDisconnect:
        return
    except Exception:
        logger.exception("websocket_error", job_id=job_id)
        await websocket.close(code=1011)


app.include_router(api_router, prefix="/api")
app.mount("/generated", StaticFiles(directory="generated_portfolios"), name="generated")
