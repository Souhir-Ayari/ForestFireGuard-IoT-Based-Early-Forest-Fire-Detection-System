"""API FastAPI — couche serveur du projet ForestFireGuard.

Lancement : uvicorn app.main:app --reload   (depuis le dossier server/)
Documentation interactive : http://localhost:8000/docs
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .database import storage
from .models import Alert, MeasurementIn, MeasurementOut
from .mqtt_client import bridge
from .risk import risk_model
from .service import process_measurement

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if bridge:
        bridge.start()
    yield
    if bridge:
        bridge.stop()


app = FastAPI(
    title="ForestFireGuard API",
    description="Détection précoce des incendies de forêt (IoT + IA)",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "storage": storage.name,
        "mqtt": {
            "enabled": bridge is not None,
            "connected": bool(bridge and bridge.connected),
            "broker": config.MQTT_BROKER,
            "topic_base": config.MQTT_TOPIC_BASE,
        },
        "ai_model_loaded": risk_model.model is not None,
    }


@app.post("/api/measurements", response_model=MeasurementOut, status_code=201)
def create_measurement(measurement: MeasurementIn):
    """Reçoit une mesure (HTTP). L'ESP32 peut aussi passer par MQTT."""
    return process_measurement(measurement)


@app.get("/api/measurements", response_model=list[MeasurementOut])
def list_measurements(limit: int = Query(50, ge=1, le=500), device_id: str | None = None):
    return storage.get_measurements(limit, device_id)


@app.get("/api/measurements/latest", response_model=MeasurementOut)
def latest_measurement(device_id: str | None = None):
    items = storage.get_measurements(1, device_id)
    if not items:
        raise HTTPException(404, "Aucune mesure reçue pour le moment")
    return items[0]


@app.get("/api/alerts", response_model=list[Alert])
def list_alerts(limit: int = Query(50, ge=1, le=500)):
    return storage.get_alerts(limit)
