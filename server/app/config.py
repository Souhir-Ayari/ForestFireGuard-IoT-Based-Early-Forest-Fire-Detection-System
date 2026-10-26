"""Configuration du serveur, lue depuis les variables d'environnement (.env)."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


# --- MQTT (communication avec l'ESP32 simulé dans Wokwi) ---
MQTT_ENABLED = _bool("MQTT_ENABLED", True)
MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
# Préfixe unique : le broker est public, il faut éviter les collisions avec d'autres projets.
MQTT_TOPIC_BASE = os.getenv("MQTT_TOPIC_BASE", "forestfireguard/souhir-ayari")

# --- Firebase (base de données) ---
USE_FIREBASE = _bool("USE_FIREBASE", False)
FIREBASE_CREDENTIALS = os.getenv(
    "FIREBASE_CREDENTIALS", str(BASE_DIR / "serviceAccountKey.json")
)

# --- Modèle IA ---
MODEL_PATH = Path(os.getenv("MODEL_PATH", str(BASE_DIR / "ml" / "model.joblib")))

# --- CORS (dashboard React) ---
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")
