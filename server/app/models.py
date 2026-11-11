"""Schémas de données (validation des mesures reçues)."""
from pydantic import BaseModel, Field


class MeasurementIn(BaseModel):
    """Mesure envoyée par un nœud ESP32. Les bornes correspondent aux capteurs."""

    device_id: str = Field(default="esp32-node-1", min_length=1, max_length=64)
    temperature: float = Field(ge=-40, le=80, description="°C (plage du DHT22)")
    humidity: float = Field(ge=0, le=100, description="% d'humidité relative")
    smoke: float = Field(ge=0, le=100, description="Niveau de fumée/gaz en % (MQ-2)")
    flame: bool = Field(default=False, description="Flamme détectée par le capteur infrarouge")


class Risk(BaseModel):
    level: int = Field(ge=0, le=2)  # 0 = faible, 1 = modéré, 2 = élevé
    label: str
    source: str  # "règles", "ia" ou "règles+ia"
    reasons: list[str] = []


class MeasurementOut(MeasurementIn):
    id: str | None = None
    timestamp: str
    risk: Risk


class Alert(BaseModel):
    id: str | None = None
    device_id: str
    timestamp: str
    level: int
    label: str
    message: str
    temperature: float
    humidity: float
    smoke: float
    flame: bool = False
