"""Vérifie la connexion à Firebase : écrit une mesure de test, la relit, puis la supprime.

Lancement (depuis server/) : python scripts/test_firebase.py
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import config  # noqa: E402


def main() -> None:
    key = Path(config.FIREBASE_CREDENTIALS)
    if not key.exists():
        sys.exit(f"ERREUR : clé Firebase introuvable : {key}\n"
                 "Place le fichier serviceAccountKey.json dans le dossier server/.")
    if not config.USE_FIREBASE:
        print("ATTENTION : USE_FIREBASE=false dans server/.env, le serveur n'utilisera pas Firebase.")

    from app.database import FirebaseStorage

    print("1. Connexion à Firebase...")
    storage = FirebaseStorage(str(key))

    print("2. Écriture d'une mesure de test dans la collection 'measurements'...")
    saved = storage.save_measurement({
        "device_id": "test-firebase",
        "temperature": 25.0,
        "humidity": 50.0,
        "smoke": 5.0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "risk": {"level": 0, "label": "faible", "source": "test", "reasons": []},
    })
    print(f"   Document créé : {saved['id']}")

    print("3. Lecture du document...")
    doc = storage._db.collection("measurements").document(saved["id"]).get()
    print(f"   Lu : {doc.to_dict()}")

    print("4. Suppression du document de test...")
    doc.reference.delete()

    print("\nOK : Firebase fonctionne (écriture, lecture et suppression).")


if __name__ == "__main__":
    main()
