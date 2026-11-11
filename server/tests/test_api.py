import os

os.environ["MQTT_ENABLED"] = "false"
os.environ["USE_FIREBASE"] = "false"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.risk import evaluate_rules  # noqa: E402

client = TestClient(app)


def test_rules_levels():
    assert evaluate_rules(24, 60, 5)[0] == 0
    assert evaluate_rules(38, 25, 10)[0] == 1
    assert evaluate_rules(30, 50, 80)[0] == 2
    assert evaluate_rules(52, 15, 10)[0] == 2


def test_flame_alone_gives_high_risk():
    level, reasons = evaluate_rules(22, 65, 0, flame=True)
    assert level == 2
    assert "flamme détectée" in reasons


def test_flame_measurement_creates_high_alert():
    base = {"device_id": "flame-node", "temperature": 22, "humidity": 65, "smoke": 2}
    assert client.post("/api/measurements", json=base).json()["flame"] is False
    r = client.post("/api/measurements", json={**base, "flame": True})
    assert r.json()["risk"]["level"] == 2
    alert = next(a for a in client.get("/api/alerts").json() if a["device_id"] == "flame-node")
    assert alert["flame"] is True
    assert "flamme" in alert["message"]


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_measurement_flow_creates_alert():
    normal = {"device_id": "test-node", "temperature": 24, "humidity": 60, "smoke": 5}
    fire = {"device_id": "test-node", "temperature": 48, "humidity": 15, "smoke": 80}

    assert client.post("/api/measurements", json=normal).json()["risk"]["level"] == 0
    r = client.post("/api/measurements", json=fire)
    assert r.status_code == 201
    assert r.json()["risk"]["label"] == "élevé"

    latest = client.get("/api/measurements/latest", params={"device_id": "test-node"}).json()
    assert latest["smoke"] == 80
    alerts = client.get("/api/alerts").json()
    assert any(a["device_id"] == "test-node" and a["level"] == 2 for a in alerts)


def test_invalid_measurement_rejected():
    r = client.post("/api/measurements", json={"temperature": 200, "humidity": 50, "smoke": 10})
    assert r.status_code == 422


def test_mqtt_message_is_processed_and_risk_published():
    import json
    from types import SimpleNamespace

    from app import config
    from app.mqtt_client import MqttBridge

    published = []
    fake_client = SimpleNamespace(publish=lambda topic, payload: published.append((topic, payload)))
    msg = SimpleNamespace(
        topic=f"{config.MQTT_TOPIC_BASE}/esp32-test/data",
        payload=json.dumps({"temperature": 25, "humidity": 55, "smoke": 90}).encode(),
    )
    MqttBridge()._on_message(fake_client, None, msg)

    assert published[0][0] == f"{config.MQTT_TOPIC_BASE}/esp32-test/risk"
    assert json.loads(published[0][1])["level"] == 2
