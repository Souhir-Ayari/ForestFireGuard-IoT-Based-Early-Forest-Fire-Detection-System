"""Couche stockage : Firebase Firestore, ou mémoire locale si Firebase n'est pas configuré.

Le stockage local permet de faire tourner et de tester tout le projet avant
d'avoir créé le projet Firebase et téléchargé la clé de service.
"""
import logging
import threading
import uuid
from collections import deque
from pathlib import Path

from . import config

log = logging.getLogger(__name__)


class LocalStorage:
    name = "local (mémoire)"

    def __init__(self, max_items: int = 2000) -> None:
        self._measurements: deque[dict] = deque(maxlen=max_items)
        self._alerts: deque[dict] = deque(maxlen=max_items)
        self._lock = threading.Lock()

    def save_measurement(self, data: dict) -> dict:
        with self._lock:
            data = {"id": uuid.uuid4().hex, **data}
            self._measurements.append(data)
            return data

    def get_measurements(self, limit: int = 50, device_id: str | None = None) -> list[dict]:
        with self._lock:
            items = [m for m in self._measurements if device_id in (None, m["device_id"])]
        return list(reversed(items[-limit:]))  # plus récent en premier

    def save_alert(self, data: dict) -> dict:
        with self._lock:
            data = {"id": uuid.uuid4().hex, **data}
            self._alerts.append(data)
            return data

    def get_alerts(self, limit: int = 50) -> list[dict]:
        with self._lock:
            return list(reversed(list(self._alerts)[-limit:]))


class FirebaseStorage:
    name = "firebase (firestore)"

    def __init__(self, credentials_path: str) -> None:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(credentials_path))
        self._db = firestore.client()
        self._query = firestore.Query

    def _save(self, collection: str, data: dict) -> dict:
        ref = self._db.collection(collection).document()
        ref.set(data)
        return {"id": ref.id, **data}

    def _list(self, collection: str, limit: int, device_id: str | None = None) -> list[dict]:
        query = self._db.collection(collection)
        if device_id:
            query = query.where("device_id", "==", device_id)
        query = query.order_by("timestamp", direction=self._query.DESCENDING).limit(limit)
        return [{"id": doc.id, **doc.to_dict()} for doc in query.stream()]

    def save_measurement(self, data: dict) -> dict:
        return self._save("measurements", data)

    def get_measurements(self, limit: int = 50, device_id: str | None = None) -> list[dict]:
        return self._list("measurements", limit, device_id)

    def save_alert(self, data: dict) -> dict:
        return self._save("alerts", data)

    def get_alerts(self, limit: int = 50) -> list[dict]:
        return self._list("alerts", limit)


def create_storage():
    if config.USE_FIREBASE:
        if Path(config.FIREBASE_CREDENTIALS).exists():
            try:
                storage = FirebaseStorage(config.FIREBASE_CREDENTIALS)
                log.info("Stockage : Firebase Firestore")
                return storage
            except Exception:
                log.exception("Connexion Firebase impossible, repli sur le stockage local")
        else:
            log.warning("Clé Firebase introuvable (%s), repli sur le stockage local",
                        config.FIREBASE_CREDENTIALS)
    log.info("Stockage : local (mémoire)")
    return LocalStorage()


storage = create_storage()
