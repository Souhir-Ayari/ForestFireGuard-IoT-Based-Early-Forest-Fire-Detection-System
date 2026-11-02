# Plan de travail — ForestFireGuard

Les tâches sont dans l'ordre où il faut les faire. Chaque phase produit quelque chose
de démontrable. ✅ = déjà fait (environnement de départ), ⬜ = à faire.

---

## Phase 0 — Préparation de l'environnement ✅

- ✅ Structure du dépôt en 4 couches (`iot/`, `server/`, base de données, `dashboard/`)
- ✅ Serveur FastAPI fonctionnel (API REST + client MQTT + règles de risque)
- ✅ Stockage avec repli local (le projet tourne même sans Firebase)
- ✅ Modèle IA Random Forest entraîné sur données synthétiques
- ✅ Circuit Wokwi (ESP32 + DHT22 + potentiomètre « fumée » + 3 LEDs + buzzer) et programme
- ✅ Dashboard React (cartes, courbes, alertes, historique)
- ✅ Simulateur de capteur Python pour tester sans Wokwi
- ✅ Tests automatiques du serveur (`pytest`)

**À faire chez toi (≈ 30 min) :** suivre la partie « Installation » du `README.md`
et vérifier que serveur + dashboard + simulateur tournent sur ton PC.

---

## Phase 1 — Couche IoT : simulation Wokwi

| # | Tâche | Résultat attendu |
|---|-------|------------------|
| 1.1 | ⬜ Créer un compte sur wokwi.com, nouveau projet **ESP32** | Projet vide |
| 1.2 | ⬜ Copier `sketch.ino`, `diagram.json`, `libraries.txt` depuis `iot/wokwi/` | Le circuit apparaît |
| 1.2 bis | ⬜ *Ou* dans VS Code : ouvrir le dossier `iot/wokwi/`, Build PlatformIO, puis « Wokwi: Start Simulator » (voir README) | Simulation locale |
| 1.3 | ⬜ Lancer la simulation, vérifier le moniteur série (WiFi OK, MQTT OK, envois toutes les 2 s) | Mesures affichées |
| 1.4 | ⬜ Changer `TOPIC_BASE` si besoin (doit être identique à `server/.env`) | Topic unique |
| 1.5 | ⬜ Tester les LEDs : cliquer sur le DHT22 / tourner le potentiomètre | Vert → jaune → rouge + buzzer |
| 1.6 | ⬜ (Bonus) Remplacer le potentiomètre par le capteur de gaz Wokwi (`wokwi-gas-sensor`) | MQ-2 simulé |
| 1.7 | ⬜ Sauvegarder le projet Wokwi et noter le lien dans le README | Lien partageable |

## Phase 2 — Couche Serveur : Python / FastAPI

| # | Tâche | Résultat attendu |
|---|-------|------------------|
| 2.1 | ⬜ Lancer le serveur, ouvrir `http://localhost:8000/docs` | Swagger visible |
| 2.2 | ⬜ Vérifier `/api/health` : `mqtt.connected = true` | Lien avec le broker |
| 2.3 | ⬜ Lancer Wokwi + serveur : les mesures de l'ESP32 arrivent dans `/api/measurements` | Chaîne IoT → serveur OK |
| 2.4 | ⬜ Vérifier que l'ESP32 reçoit le risque renvoyé (`Serveur -> risque ...` dans le moniteur série) | Boucle complète |
| 2.5 | ⬜ Ajuster les seuils des règles dans `server/app/risk.py` | Règles justifiées |
| 2.6 | ⬜ (Bonus) Détecter un capteur muet (pas de mesure depuis X s) → alerte « capteur hors ligne » | Robustesse |

## Phase 3 — Couche Base de données : Firebase

Voir le guide pas à pas : [`docs/FIREBASE.md`](FIREBASE.md).

| # | Tâche | Résultat attendu |
|---|-------|------------------|
| 3.1 | ⬜ Créer le projet Firebase + base **Firestore** | Console Firebase |
| 3.2 | ⬜ Générer la clé de compte de service → `server/serviceAccountKey.json` | Fichier présent (jamais commité) |
| 3.3 | ⬜ Mettre `USE_FIREBASE=true` dans `server/.env`, relancer | `/api/health` → `storage: firebase` |
| 3.4 | ⬜ Vérifier les collections `measurements` et `alerts` dans la console | Données visibles |
| 3.5 | ⬜ Créer l'index composite demandé par Firestore (lien dans le message d'erreur) pour le filtre `device_id` | Requêtes OK |

## Phase 4 — Couche Interface : Dashboard React

| # | Tâche | Résultat attendu |
|---|-------|------------------|
| 4.1 | ⬜ Lancer `npm run dev`, ouvrir `http://localhost:5173` | Dashboard en direct |
| 4.2 | ⬜ Personnaliser (logo, couleurs, titre) | Identité du projet |
| 4.3 | ⬜ (Bonus) Filtre par capteur, choix de la période | Ergonomie |
| 4.4 | ⬜ (Bonus) Notification sonore / visuelle à l'arrivée d'une alerte | Alerte visible |

## Phase 5 — Intelligence artificielle

| # | Tâche | Résultat attendu |
|---|-------|------------------|
| 5.1 | ⬜ Comprendre et justifier le jeu de données dans `server/ml/train_model.py` | Hypothèses écrites |
| 5.2 | ⬜ (Mieux) Enregistrer de vraies séries depuis Wokwi/Firebase et les étiqueter | Dataset propre |
| 5.3 | ⬜ Réentraîner, comparer Random Forest / arbre de décision / règles seules | Tableau comparatif |
| 5.4 | ⬜ Garder la matrice de confusion et les faux positifs/négatifs pour le rapport | Résultats chiffrés |

## Phase 6 — Évaluation et démonstration

| # | Tâche | Résultat attendu |
|---|-------|------------------|
| 6.1 | ⬜ Jouer les 4 scénarios du sujet (normal, vigilance, fumée, consultation) | Captures d'écran |
| 6.2 | ⬜ Mesurer faux positifs / faux négatifs sur des scénarios scriptés (`simulate_sensor.py`) | Tableau d'évaluation |
| 6.3 | ⬜ Mesurer le délai capteur → alerte sur le dashboard | Latence en secondes |
| 6.4 | ⬜ Rédiger le rapport + préparer les slides | Livrables |

---

## Pour la séance de demain : quoi montrer au professeur

1. **L'architecture** (schéma du `README.md`) : 4 couches et le flux de données.
2. **Le circuit Wokwi** : ESP32, DHT22, potentiomètre, LEDs, buzzer.
3. **Le serveur** : `http://localhost:8000/docs` (Swagger) et `/api/health`.
4. **La démo de bout en bout** avec le simulateur :
   ```bash
   python scripts/simulate_sensor.py --scenario demo
   ```
   Le dashboard passe de **faible** à **modéré** puis **élevé**, et les alertes apparaissent.
5. **Le modèle IA** : `python ml/train_model.py` affiche le rapport et la matrice de confusion.
6. **La suite** : phases 3 à 6 ci-dessus (Firebase, données réelles, évaluation).
