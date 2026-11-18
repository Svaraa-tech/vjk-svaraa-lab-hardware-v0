"""Svaraa V0 Lab API — board + simulator + SIM product ingest."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .adapters_routes import router as adapters_router
from .board_routes import router as board_router
from .hardware_routes import router as hardware_router
from .product_routes import router as product_router
from .protocol_routes import router as protocol_router
from .sim_routes import router as sim_router
from .wokwi_routes import router as wokwi_router

app = FastAPI(
    title="Svaraa V0 Lab API",
    version="0.3.0",
    description="SIM profile local development API. notification_provider=mock.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(board_router)
app.include_router(sim_router)
app.include_router(adapters_router)
app.include_router(hardware_router)
app.include_router(protocol_router)
app.include_router(wokwi_router)
app.include_router(product_router)


@app.get("/v1/health")
def product_health():
    return {
        "status": "ok",
        "service": "svaraa-v0-api",
        "profile": "SIM",
        "notification_provider": "mock",
        "note": "Liveness only; not whole-device health.",
    }


@app.get("/lab/v1/health")
def lab_health():
    return {
        "status": "ok",
        "namespace": "lab",
        "profile": "SIM",
        "simulated": True,
        "board": True,
        "simulator": True,
        "notification_provider": "mock",
    }
