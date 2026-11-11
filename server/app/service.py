"""Traitement d'une mesure : évaluation du risque, enregistrement, création d'alertes.

Utilisé à la fois par l'API HTTP et par le client MQTT.
"""
import logging
import threading
from datetime import datetime, timezone

from .database import storage
from .models import MeasurementIn
from .risk import evaluate

log = logging.getLogger(__name__)

# Dernier niveau connu par capteur : on crée une alerte seulement quand le niveau monte
_last_level: dict[str, int] = {}
_lock = threading.Lock()


def process_measurement(measurement: MeasurementIn) -> dict:
    data = measurement.model_dump()
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    data["risk"] = evaluate(data["temperature"], data["humidity"], data["smoke"], data["flame"])
    saved = storage.save_measurement(data)

    level = data["risk"]["level"]
    with _lock:
        previous = _last_level.get(measurement.device_id, 0)
        _last_level[measurement.device_id] = level

    if level > previous:
        reasons = ", ".join(data["risk"]["reasons"]) or "conditions suspectes"
        storage.save_alert({
            "device_id": measurement.device_id,
            "timestamp": data["timestamp"],
            "level": level,
            "label": data["risk"]["label"],
            "message": f"Risque {data['risk']['label']} : {reasons}",
            "temperature": data["temperature"],
            "humidity": data["humidity"],
            "smoke": data["smoke"],
            "flame": data["flame"],
        })
        log.warning("ALERTE %s sur %s : %s", data["risk"]["label"], measurement.device_id, reasons)

    return saved
