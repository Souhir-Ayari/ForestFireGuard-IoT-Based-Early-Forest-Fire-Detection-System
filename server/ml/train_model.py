"""Entraînement du modèle IA (Random Forest) de classification du risque.

1. Génère un jeu de données synthétique (scénarios normal / vigilance / feu).
2. Entraîne un Random Forest et l'évalue (matrice de confusion, faux positifs/négatifs).
3. Sauvegarde le modèle dans ml/model.joblib (chargé automatiquement par le serveur).

Lancement (depuis server/) : python ml/train_model.py
"""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

ML_DIR = Path(__file__).resolve().parent
RNG = np.random.default_rng(42)
LABELS = ["faible", "modéré", "élevé"]


def generate(n: int, temp, hum, smoke, label: int) -> pd.DataFrame:
    return pd.DataFrame({
        "temperature": RNG.normal(*temp, n).clip(-40, 80),
        "humidity": RNG.normal(*hum, n).clip(0, 100),
        "smoke": RNG.normal(*smoke, n).clip(0, 100),
        "risk": label,
    })


def build_dataset() -> pd.DataFrame:
    # (moyenne, écart-type) par scénario — à remplacer/compléter par des données réelles
    parts = [
        generate(1500, (24, 5), (60, 12), (8, 5), 0),    # normal
        generate(800, (30, 4), (45, 8), (15, 6), 0),     # journée chaude mais sans danger
        generate(1000, (38, 3), (25, 5), (20, 7), 1),    # vigilance : chaud et sec
        generate(500, (30, 5), (45, 10), (40, 6), 1),    # un peu de fumée
        generate(1000, (45, 6), (18, 6), (70, 12), 2),   # départ de feu
        generate(400, (55, 4), (12, 4), (35, 10), 2),    # chaleur extrême
    ]
    return pd.concat(parts, ignore_index=True).sample(frac=1, random_state=42)


def main() -> None:
    df = build_dataset()
    df.to_csv(ML_DIR / "dataset.csv", index=False)

    X, y = df[["temperature", "humidity", "smoke"]], df["risk"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    model.fit(X_train.values, y_train)
    y_pred = model.predict(X_test.values)

    print(classification_report(y_test, y_pred, target_names=LABELS))
    cm = confusion_matrix(y_test, y_pred)
    print("Matrice de confusion (lignes = réel, colonnes = prédit) :")
    print(pd.DataFrame(cm, index=LABELS, columns=LABELS))

    # Vue « alerte » : risque élevé vs reste
    fp = int(((y_pred == 2) & (y_test != 2)).sum())
    fn = int(((y_pred != 2) & (y_test == 2)).sum())
    print(f"\nAlerte (risque élevé) : {fp} faux positifs, {fn} faux négatifs "
          f"sur {len(y_test)} échantillons de test")

    joblib.dump(model, ML_DIR / "model.joblib")
    print(f"Modèle sauvegardé dans {ML_DIR / 'model.joblib'}")


if __name__ == "__main__":
    main()
