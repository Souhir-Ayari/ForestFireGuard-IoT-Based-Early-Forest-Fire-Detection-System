# 🌲 ForestFireGuard — Détection précoce des incendies de forêt (IoT + IA)

Projet IoT : un nœud ESP32 simulé dans **Wokwi** mesure la température, l'humidité et la fumée,
un serveur **FastAPI** évalue le niveau de risque (règles + **Random Forest**), les données sont
stockées dans **Firebase**, et un **dashboard React** affiche les mesures, les courbes et les alertes.

> 🚀 **Débutant / Windows ? Suivre [`docs/GUIDE_LANCEMENT.md`](docs/GUIDE_LANCEMENT.md)** : lancement par double-clic sur les fichiers `.bat`.
>
> 📋 Plan de travail détaillé : [`docs/PLAN_DE_TRAVAIL.md`](docs/PLAN_DE_TRAVAIL.md)
>
> 🗓️ Nouvelles fonctionnalités, jour par jour : [`docs/PLAN_FONCTIONNALITES.md`](docs/PLAN_FONCTIONNALITES.md)

## Architecture

```
┌──────────────────────┐   MQTT (broker public)    ┌──────────────────────────┐
│ 1. COUCHE IoT        │  .../<device>/data  ───▶  │ 2. COUCHE SERVEUR        │
│ Wokwi : ESP32        │                           │ Python FastAPI (local)   │
│ DHT22, MQ-2, flamme  │  ◀───  .../<device>/risk  │ validation, règles, IA   │
│ LEDs + buzzer        │                           └────────────┬─────────────┘
└──────────────────────┘                                        │
                                                                ▼
┌──────────────────────┐      HTTP REST (JSON)     ┌──────────────────────────┐
│ 4. COUCHE INTERFACE  │  ◀──────────────────────  │ 3. COUCHE BASE DE DONNÉES│
│ Dashboard React      │       /api/measurements   │ Firebase Firestore       │
│ cartes, courbes,     │       /api/alerts         │ (repli : mémoire locale) │
│ alertes, historique  │                           └──────────────────────────┘
└──────────────────────┘
```

**Pourquoi MQTT ?** La simulation tourne sur wokwi.com (dans le cloud) et ne peut pas joindre
directement `localhost`. L'ESP32 et le serveur local se connectent donc tous les deux à un
broker MQTT public (`broker.hivemq.com`), qui relaie les messages dans les deux sens.

| Niveau | Couleur | LED | Exemple de condition |
|--------|---------|-----|----------------------|
| 0 — faible | vert | verte | valeurs normales |
| 1 — modéré (vigilance) | jaune | jaune | ≥ 35 °C et ≤ 30 % d'humidité, ou fumée ≥ 30 % |
| 2 — élevé (alerte) | rouge | rouge + buzzer | flamme détectée, ou fumée ≥ 60 %, ou ≥ 50 °C et ≤ 20 % d'humidité |

## Arborescence

```
iot/wokwi/        sketch.ino, diagram.json, libraries.txt  (couche IoT)
                  + platformio.ini, wokwi.toml  (simulation dans VS Code)
server/app/       API FastAPI, MQTT, règles de risque, stockage  (couche serveur)
server/ml/        entraînement du modèle IA (Random Forest)
server/scripts/   simulate_sensor.py : simulateur de capteur (sans Wokwi)
server/tests/     tests automatiques (pytest)
dashboard/        application React + Vite  (couche interface)
docs/             plan de travail, guide Firebase
```

## Installation (une seule fois)

Prérequis : **Python 3.10+**, **Node.js 18+**, Git.

```bash
# Serveur
cd server
python -m venv .venv
# Windows : .venv\Scripts\activate      Linux/macOS : source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # Windows : copy .env.example .env
python ml/train_model.py          # crée ml/model.joblib

# Dashboard
cd ../dashboard
npm install
```

## Lancement

Ouvrir **3 terminaux** :

```bash
# Terminal 1 — serveur (dans server/, venv activé)
uvicorn app.main:app --reload
#   API : http://localhost:8000/docs     état : http://localhost:8000/api/health

# Terminal 2 — dashboard (dans dashboard/)
npm run dev
#   http://localhost:5173

# Terminal 3 — source de données : au choix
#  a) Wokwi : sur wokwi.com, nouveau projet ESP32, coller les 3 fichiers de iot/wokwi/, ▶
#  b) Simulateur (dans server/, venv activé) :
python scripts/simulate_sensor.py --scenario demo         # normal → vigilance → feu
python scripts/simulate_sensor.py --mode mqtt --scenario fire
```

### Wokwi dans VS Code (optionnel, PlatformIO)

L'extension Wokwi de VS Code ne compile pas le code : elle simule le firmware compilé par
**PlatformIO**, indiqué dans `iot/wokwi/wokwi.toml`.

1. Installer les extensions **PlatformIO IDE** et **Wokwi Simulator** dans VS Code.
2. Activer la licence Wokwi (gratuite) : `F1` → **Wokwi: Request a New License**.
3. **Fichier → Ouvrir le dossier… → `iot/wokwi/`** (ce dossier doit être la racine du workspace,
   sinon l'extension affiche « wokwi.toml configuration file not found in workspace »).
4. Compiler : bouton ✓ **Build** de PlatformIO (ou `pio run`). Le premier build télécharge
   la plateforme ESP32 et les bibliothèques (quelques minutes).
5. `F1` → **Wokwi: Start Simulator**.

Après chaque modification de `sketch.ino`, recompiler (étape 4) avant de relancer la simulation.

Dans Wokwi, pendant la simulation, cliquer sur un capteur pour changer sa valeur :
le **DHT22** (température/humidité), le **capteur de gaz MQ-2** (fumée) et le
**capteur de flamme**. Les LEDs et le buzzer suivent le niveau de risque.

## Tests

```bash
cd server && python -m pytest -q
```

## API

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/health` | état du serveur, de MQTT, de la base et du modèle IA |
| POST | `/api/measurements` | envoyer une mesure `{device_id, temperature, humidity, smoke}` |
| GET | `/api/measurements?limit=50&device_id=` | historique (plus récent en premier) |
| GET | `/api/measurements/latest` | dernière mesure |
| GET | `/api/alerts?limit=50` | historique des alertes |

## Configuration

- `server/.env` : broker MQTT, topic, Firebase, modèle IA (voir `.env.example`).
- `iot/wokwi/sketch.ino` : `TOPIC_BASE` **doit être identique** à `MQTT_TOPIC_BASE` du serveur.
- Firebase : voir [`docs/FIREBASE.md`](docs/FIREBASE.md). Sans clé, le serveur garde les données en mémoire.

## Limites

Prototype pédagogique (preuve de concept) : le modèle est entraîné sur des données synthétiques
et le broker MQTT public n'est pas sécurisé. Une validation avec des capteurs réels serait
nécessaire avant toute utilisation opérationnelle.

---
Projet IoT — Souhir Ayari
