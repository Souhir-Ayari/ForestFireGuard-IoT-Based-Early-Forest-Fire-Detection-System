"""Simulateur de capteur : envoie des mesures au serveur sans passer par Wokwi.

Pratique pour tester le serveur et le dashboard, et pour la démonstration.

Exemples (depuis server/) :
  python scripts/simulate_sensor.py --scenario demo      # normal -> vigilance -> feu
  python scripts/simulate_sensor.py --scenario normal --count 20
  python scripts/simulate_sensor.py --mode mqtt --scenario fire
"""
import argparse
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

SCENARIOS = {
    # (température, humidité, fumée) cibles
    "normal": (24, 60, 8),
    "vigilance": (38, 25, 20),
    "fire": (48, 15, 75),
}


def reading(scenario: str, device_id: str) -> dict:
    t, h, s = SCENARIOS[scenario]
    return {
        "device_id": device_id,
        "temperature": round(t + random.uniform(-1.5, 1.5), 1),
        "humidity": round(min(100, max(0, h + random.uniform(-3, 3))), 1),
        "smoke": round(min(100, max(0, s + random.uniform(-3, 3))), 1),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=[*SCENARIOS, "demo"], default="demo")
    parser.add_argument("--count", type=int, default=10, help="mesures par scénario")
    parser.add_argument("--interval", type=float, default=2.0, help="secondes entre mesures")
    parser.add_argument("--mode", choices=["http", "mqtt"], default="http")
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--device", default="simulateur-1")
    args = parser.parse_args()

    steps = ["normal", "vigilance", "fire"] if args.scenario == "demo" else [args.scenario]

    if args.mode == "mqtt":
        import paho.mqtt.client as mqtt

        from app import config

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.connect(config.MQTT_BROKER, config.MQTT_PORT)
        client.loop_start()
        topic = f"{config.MQTT_TOPIC_BASE}/{args.device}/data"

        def send(data):
            client.publish(topic, json.dumps(data)).wait_for_publish()
            return f"publié sur {topic}"
    else:
        import requests

        def send(data):
            r = requests.post(f"{args.url}/api/measurements", json=data, timeout=5)
            r.raise_for_status()
            return f"risque {r.json()['risk']['label']}"

    for scenario in steps:
        print(f"--- Scénario : {scenario} ---")
        for _ in range(args.count):
            data = reading(scenario, args.device)
            print(data, "->", send(data))
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
