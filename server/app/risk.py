"""Évaluation du niveau de risque : règles de sécurité + modèle IA (optionnel)."""
import logging

from . import config

log = logging.getLogger(__name__)

LABELS = {0: "faible", 1: "modéré", 2: "élevé"}

# Seuils des règles de sécurité (à ajuster pendant les tests)
SMOKE_HIGH = 60
SMOKE_MEDIUM = 30
TEMP_HIGH = 50
TEMP_MEDIUM = 35
HUMIDITY_LOW = 30
HUMIDITY_VERY_LOW = 20


def evaluate_rules(temperature: float, humidity: float, smoke: float) -> tuple[int, list[str]]:
    """Règles simples et explicables. Retourne (niveau, raisons)."""
    reasons: list[str] = []
    level = 0

    if smoke >= SMOKE_HIGH:
        level = 2
        reasons.append(f"fumée très élevée ({smoke:.0f} %)")
    elif smoke >= SMOKE_MEDIUM:
        level = max(level, 1)
        reasons.append(f"présence de fumée ({smoke:.0f} %)")

    if temperature >= TEMP_HIGH and humidity <= HUMIDITY_VERY_LOW:
        level = 2
        reasons.append(f"chaleur extrême et air très sec ({temperature:.1f} °C, {humidity:.0f} %)")
    elif temperature >= TEMP_MEDIUM and humidity <= HUMIDITY_LOW:
        level = max(level, 1)
        reasons.append(f"chaleur et air sec ({temperature:.1f} °C, {humidity:.0f} %)")
    elif temperature >= TEMP_HIGH:
        level = max(level, 1)
        reasons.append(f"température très élevée ({temperature:.1f} °C)")

    return level, reasons


class RiskModel:
    """Charge le modèle scikit-learn s'il existe (créé par ml/train_model.py)."""

    def __init__(self) -> None:
        self.model = None
        self.load()

    def load(self) -> None:
        if config.MODEL_PATH.exists():
            import joblib

            self.model = joblib.load(config.MODEL_PATH)
            log.info("Modèle IA chargé depuis %s", config.MODEL_PATH)
        else:
            log.warning("Aucun modèle IA trouvé (%s) : règles seules", config.MODEL_PATH)

    def predict(self, temperature: float, humidity: float, smoke: float) -> int | None:
        if self.model is None:
            return None
        return int(self.model.predict([[temperature, humidity, smoke]])[0])


risk_model = RiskModel()


def evaluate(temperature: float, humidity: float, smoke: float) -> dict:
    """Combine règles et IA : on garde le niveau le plus prudent (le plus élevé)."""
    rule_level, reasons = evaluate_rules(temperature, humidity, smoke)
    ml_level = risk_model.predict(temperature, humidity, smoke)

    if ml_level is None:
        level, source = rule_level, "règles"
    else:
        level, source = max(rule_level, ml_level), "règles+ia"
        if ml_level > rule_level:
            reasons.append(f"le modèle IA estime un risque {LABELS[ml_level]}")

    return {"level": level, "label": LABELS[level], "source": source, "reasons": reasons}
