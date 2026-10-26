"""Client MQTT : reçoit les mesures de l'ESP32 (Wokwi) et lui renvoie le niveau de risque.

Topics (préfixe = MQTT_TOPIC_BASE) :
  <préfixe>/<device_id>/data  <- mesures JSON publiées par l'ESP32
  <préfixe>/<device_id>/risk  -> niveau de risque renvoyé par le serveur
"""
import json
import logging

import paho.mqtt.client as mqtt
from pydantic import ValidationError

from . import config
from .models import MeasurementIn
from .service import process_measurement

log = logging.getLogger(__name__)


class MqttBridge:
    def __init__(self) -> None:
        self.connected = False
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

    def start(self) -> None:
        log.info("Connexion MQTT à %s:%s", config.MQTT_BROKER, config.MQTT_PORT)
        self.client.connect_async(config.MQTT_BROKER, config.MQTT_PORT, keepalive=30)
        self.client.loop_start()

    def stop(self) -> None:
        self.client.loop_stop()
        self.client.disconnect()

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        self.connected = not reason_code.is_failure
        if self.connected:
            topic = f"{config.MQTT_TOPIC_BASE}/+/data"
            client.subscribe(topic)
            log.info("MQTT connecté, abonné à %s", topic)
        else:
            log.error("Échec de connexion MQTT : %s", reason_code)

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.connected = False
        log.warning("MQTT déconnecté (%s)", reason_code)

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload)
            payload.setdefault("device_id", msg.topic.split("/")[-2])
            result = process_measurement(MeasurementIn(**payload))
        except (json.JSONDecodeError, ValidationError) as exc:
            log.warning("Message MQTT invalide sur %s : %s", msg.topic, exc)
            return
        except Exception:
            log.exception("Erreur lors du traitement du message MQTT")
            return

        risk = result["risk"]
        response = json.dumps({"level": risk["level"], "label": risk["label"]})
        client.publish(f"{config.MQTT_TOPIC_BASE}/{result['device_id']}/risk", response)


bridge = MqttBridge() if config.MQTT_ENABLED else None
