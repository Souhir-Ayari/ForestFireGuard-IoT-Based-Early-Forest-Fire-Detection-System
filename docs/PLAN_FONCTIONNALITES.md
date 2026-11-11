# Plan des nouvelles fonctionnalités — ForestFireGuard

Ce plan prolonge [`PLAN_DE_TRAVAIL.md`](PLAN_DE_TRAVAIL.md) (la base des 4 couches est terminée).
Il découpe les nouvelles fonctionnalités en **18 jours** d'environ **2 à 4 h** chacun.
Chaque jour se termine par quelque chose qui marche et qu'on peut montrer.

Légende : ⬜ à faire · 🔄 en cours · ✅ terminé

---

## Vue d'ensemble

| Bloc | Jour | Fonctionnalité | Couches touchées |
|------|------|----------------|------------------|
| **A. Nouveaux capteurs** | J1 | ⬜ Capteur de gaz MQ-2 + capteur de flamme | IoT, serveur, dashboard |
| | J2 | ⬜ Vitesse du vent et risque de propagation | IoT, serveur, dashboard |
| | J3 | ⬜ Écran LCD sur l'ESP32 | IoT |
| **B. Réseau de capteurs** | J4 | ⬜ Fiche capteur (collection `devices`) | serveur, Firebase, dashboard |
| | J5 | ⬜ Plusieurs ESP32 (zones nord, sud, est) | IoT, serveur |
| | J6 | ⬜ Détection de capteur hors ligne | serveur, Firebase, dashboard |
| **C. Dashboard** | J7 | ⬜ Carte interactive de la forêt | dashboard |
| | J8 | ⬜ Page de détail d'un capteur | dashboard, serveur |
| | J9 | ⬜ Alerte visuelle (écran rouge) et sonore | dashboard |
| **D. Gestion des alertes** | J10 | ⬜ Suivi des alertes : nouvelle → vue → traitée + commentaire | serveur, Firebase, dashboard |
| | J11 | ⬜ Notifications Telegram et e-mail | serveur |
| | J12 | ⬜ Commandes à distance vers l'ESP32 | IoT, serveur, dashboard |
| **E. Données externes** | J13 | ⬜ Météo réelle (OpenWeatherMap) comparée aux capteurs | serveur, dashboard |
| **F. Sécurité** | J14 | ⬜ Authentification (Firebase Authentication) | serveur, dashboard |
| **G. Intelligence artificielle** | J15 | ⬜ Collecte et étiquetage de vraies données | serveur, Firebase |
| | J16 | ⬜ Nouveau modèle IA (5 capteurs) + comparaison | serveur |
| **H. Finalisation** | J17 | ⬜ Évaluation des scénarios | tout |
| | J18 | ⬜ Rapport, slides, répétition de la démo | — |

### Pourquoi cet ordre ?

```
A. Capteurs ──▶ B. Réseau de capteurs ──▶ C. Dashboard ──▶ D. Alertes ──▶ E. Météo
     │                  │                                                    │
     │                  └── la carte, la page détail, le hors-ligne          │
     │                      et la météo ont besoin des fiches capteurs (GPS) │
     │                                                                       ▼
     └── l'IA a besoin de la liste FINALE des capteurs ───────────▶ G. IA ──▶ H. Fin
                                                                     ▲
                                             F. Authentification ────┘
```

- **Les capteurs d'abord (A)** : ajouter flamme et vent change le format des mesures. Tout ce qui suit
  (dashboard, IA) doit être construit sur le format final, sinon il faudra le refaire.
- **Les fiches capteurs avant la carte (B → C)** : la carte, la page détail, la détection hors ligne et
  la météo ont toutes besoin du nom, de la zone et des coordonnées GPS de chaque capteur.
- **L'authentification vers la fin (F)** : elle protège les actions sensibles (commandes à distance,
  traitement des alertes, modification des fiches). On l'ajoute une fois ces actions créées, pour ne pas
  devoir se reconnecter à chaque test pendant le développement.
- **L'IA à la fin (G)** : le modèle doit être entraîné sur les 5 mesures finales
  (température, humidité, fumée, flamme, vent) et sur de vraies données collectées pendant les jours précédents.

> Les jours peuvent être déplacés à l'intérieur d'un même bloc. Entre blocs, respecter les flèches
> ci-dessus évite de refaire du travail.

---

## Bloc A — Nouveaux capteurs

### J1 — Capteur de gaz MQ-2 + capteur de flamme

**Objectif** : remplacer le potentiomètre par un vrai capteur de gaz simulé et ajouter la détection de flamme.

| Couche | Tâches |
|--------|--------|
| IoT | Remplacer `wokwi-potentiometer` par `wokwi-gas-sensor` (sortie AOUT → D34) dans `diagram.json`. Ajouter un capteur de flamme (`wokwi-flame-sensor`, sortie DOUT → une broche libre, ex. D32). Envoyer `"flame": true/false` dans le JSON. Mettre à jour les règles locales. |
| Serveur | Ajouter le champ `flame: bool` dans `models.py`. Règle : flamme détectée → risque **élevé** immédiat. Ajouter un test. |
| Dashboard | Nouvelle carte « Flamme : détectée / aucune ». |
| Simulateur | Ajouter `flame` aux scénarios (`fire` → `true`). |

**Terminé quand** : dans Wokwi, augmenter le gaz fait monter la fumée sur le dashboard, et activer la
flamme fait passer le risque à **élevé** avec la LED rouge et le buzzer.

### J2 — Vitesse du vent et risque de propagation

**Objectif** : un vent fort aggrave le risque, car le feu se propage plus vite.

| Couche | Tâches |
|--------|--------|
| IoT | Ajouter un potentiomètre « anémomètre » (→ D35), converti en 0–100 km/h. Envoyer `"wind"`. |
| Serveur | Champ `wind` (0–100 km/h). Règle : si le vent dépasse 30 km/h et que le risque est déjà modéré, il monte d'un cran, avec la raison « vent fort : propagation rapide ». |
| Dashboard | Carte « Vent (km/h) » et courbe du vent sur le graphique. |

**Terminé quand** : les conditions de vigilance plus un vent fort donnent un risque **élevé** sur le dashboard.

### J3 — Écran LCD sur l'ESP32

**Objectif** : afficher l'état directement sur le boîtier, comme un vrai capteur de terrain.

| Couche | Tâches |
|--------|--------|
| IoT | Ajouter `wokwi-lcd1602` en mode I2C (SDA → D21, SCL → D22) et la bibliothèque `LiquidCrystal I2C`. Ligne 1 : `24.1C 58% F:12%`. Ligne 2 : `Risque: FAIBLE` (ou `HORS LIGNE` si le serveur ne répond plus). Ajouter la bibliothèque dans `libraries.txt` **et** `platformio.ini`. |

**Terminé quand** : l'écran affiche les mesures et le niveau de risque renvoyé par le serveur.

---

## Bloc B — Réseau de capteurs

### J4 — Fiche capteur (collection `devices`)

**Objectif** : chaque capteur a une fiche (nom, zone, coordonnées GPS, date d'installation, état).

| Couche | Tâches |
|--------|--------|
| Firebase | Nouvelle collection `devices` : `{ id, name, zone, lat, lng, installed_at, status: "en ligne" / "hors ligne" / "maintenance", last_seen }`. |
| Serveur | Routes `GET /api/devices`, `GET /api/devices/{id}`, `POST /api/devices`, `PUT /api/devices/{id}`. Mise à jour de `last_seen` à chaque mesure. Un capteur inconnu est créé automatiquement avec le statut « à configurer ». Script `scripts/seed_devices.py` qui crée 3 capteurs (nord, sud, est) avec de vraies coordonnées d'une forêt tunisienne (ex. Aïn Draham). |
| Dashboard | Liste des capteurs avec leur zone et leur état. |

**Terminé quand** : les 3 fiches sont visibles dans Firestore et sur le dashboard.

### J5 — Plusieurs ESP32 (zones nord, sud, est)

**Objectif** : simuler une vraie forêt couverte par plusieurs nœuds.

| Couche | Tâches |
|--------|--------|
| IoT | Rendre `DEVICE_ID` facile à changer en haut de `sketch.ino` (`esp32-nord`, `esp32-sud`, `esp32-est`). Lancer **1 ESP32 dans VS Code + 1 ou 2 dans des onglets wokwi.com**, chacun avec son `DEVICE_ID`. L'extension VS Code ne lance qu'une simulation à la fois. |
| Simulateur | Option `--devices esp32-nord,esp32-sud,esp32-est` : un scénario différent par zone (ex. feu seulement au sud). |
| Dashboard | Les cartes du haut affichent un résumé par capteur, ou un sélecteur de capteur. |

**Terminé quand** : 3 capteurs envoient en même temps, et on voit lequel est en danger.

### J6 — Détection de capteur hors ligne

**Objectif** : un capteur qui ne répond plus est suspect (panne, batterie, ou capteur détruit par le feu).

| Couche | Tâches |
|--------|--------|
| Serveur | Tâche de fond toutes les 10 s : si `last_seen` date de plus de 30 s, le statut passe à « hors ligne » et une alerte de type `hors_ligne` est créée (une seule fois). Au retour d'une mesure, le statut repasse à « en ligne ». Ajouter un test. |
| Dashboard | Capteur hors ligne affiché en gris, avec « vu il y a X min ». |

**Terminé quand** : arrêter une simulation Wokwi fait apparaître une alerte « capteur hors ligne » en moins d'une minute.

---

## Bloc C — Dashboard

### J7 — Carte interactive de la forêt 🗺️

**Objectif** : voir d'un coup d'œil où se trouve le danger.

| Couche | Tâches |
|--------|--------|
| Dashboard | Installer `leaflet` et `react-leaflet`. Fond de carte OpenStreetMap. Un marqueur par capteur (coordonnées GPS des fiches), coloré selon le risque : vert, jaune, rouge, ou gris si hors ligne. Au clic, une bulle avec les dernières valeurs et un lien vers la page du capteur. Zone rouge clignotante autour d'un capteur en alerte. |

**Terminé quand** : la carte se met à jour en direct pendant le scénario « feu au sud ».

### J8 — Page de détail d'un capteur

**Objectif** : tout savoir sur un capteur.

| Couche | Tâches |
|--------|--------|
| Dashboard | Installer `react-router-dom`. Page `/capteurs/:id` : fiche (nom, zone, GPS, date d'installation, état), courbes de ce capteur seul, ses alertes, choix de la période (1 h / 24 h / 7 jours). |
| Serveur | Paramètre `since` sur `/api/measurements`. Créer l'index Firestore demandé (`device_id` + `timestamp`, voir `FIREBASE.md`). |

**Terminé quand** : un clic sur un capteur (carte ou liste) ouvre sa page avec ses propres données.

### J9 — Alerte visuelle et sonore

**Objectif** : impossible de rater une alerte.

| Couche | Tâches |
|--------|--------|
| Dashboard | À l'arrivée d'une nouvelle alerte **élevée** : bandeau rouge clignotant en haut, bip répété (Web Audio API), titre de l'onglet qui clignote (« 🔥 ALERTE »). Bouton « Activer le son », car les navigateurs bloquent le son tant qu'on n'a pas cliqué sur la page. Bouton « J'ai vu » qui arrête le son. |

**Terminé quand** : pendant le scénario feu, l'écran clignote et sonne jusqu'au clic sur « J'ai vu ».

---

## Bloc D — Gestion des alertes

### J10 — Suivi des alertes : nouvelle → vue → traitée

**Objectif** : suivre le traitement de chaque alerte, comme un vrai centre de surveillance.

| Couche | Tâches |
|--------|--------|
| Firebase | Champs ajoutés aux `alerts` : `status` (`nouvelle` / `vue` / `traitée`), `comment`, `updated_at`, plus tard `updated_by` (J14). |
| Serveur | `PATCH /api/alerts/{id}` avec `{status, comment}`. Filtre `?status=nouvelle`. Ajouter un test. |
| Dashboard | Boutons « Marquer vue » et « Traiter » (avec zone de commentaire). Compteur d'alertes non traitées. Le bouton « J'ai vu » du J9 passe l'alerte en « vue ». |

**Terminé quand** : une alerte passe par les 3 états, et son commentaire est visible dans Firestore.

### J11 — Notifications Telegram et e-mail 📩

**Objectif** : prévenir les responsables même quand personne ne regarde le dashboard.

| Couche | Tâches |
|--------|--------|
| Préparation | Créer un bot Telegram avec **@BotFather** (gratuit) et récupérer le token et ton `chat_id`. Pour l'e-mail : un « mot de passe d'application » Gmail. Tout va dans `server/.env`, **jamais sur GitHub**. |
| Serveur | Module `notifications.py` : un message Telegram et un e-mail pour chaque alerte **élevée** ou **hors ligne**, avec le capteur, la zone, les valeurs et un lien Google Maps. Anti-spam : au maximum un message par capteur toutes les 5 min. Les notifications sont désactivées si les clés sont absentes. |

**Terminé quand** : pendant la démo, le téléphone reçoit le message Telegram au passage en rouge.

### J12 — Commandes à distance

**Objectif** : agir sur un capteur depuis le dashboard.

| Couche | Tâches |
|--------|--------|
| IoT | S'abonner au topic `<préfixe>/<device_id>/cmd`. Commandes : `silence` (couper le buzzer 5 min), `interval` (changer la fréquence d'envoi), `test` (allumer toutes les LEDs 3 s), `reboot`. Répondre sur `.../cmd_ack`. |
| Serveur | `POST /api/devices/{id}/commands` qui publie sur MQTT. Historique des commandes dans Firestore (`commands`). |
| Dashboard | Boutons sur la page du capteur (J8), avec la confirmation reçue de l'ESP32. |

**Terminé quand** : un clic sur « Couper le buzzer » arrête le buzzer dans Wokwi.

---

## Bloc E — Données externes

### J13 — Météo réelle (OpenWeatherMap)

**Objectif** : comparer les capteurs à la météo officielle, pour repérer un capteur défaillant ou une chaleur locale anormale.

| Couche | Tâches |
|--------|--------|
| Préparation | Créer un compte gratuit sur openweathermap.org et une clé API. ⚠️ L'activation de la clé peut prendre jusqu'à 2 h : la créer **la veille**. Clé dans `server/.env`. |
| Serveur | Module `weather.py` : toutes les 10 min, météo actuelle (température, humidité, vent) pour les coordonnées GPS de chaque capteur. Cache en mémoire et stockage dans la collection `weather`. Route `GET /api/devices/{id}/weather`. Écart signalé si le capteur indique plus de 15 °C au-dessus de la météo (« chaleur locale anormale »). |
| Dashboard | Bloc « Capteur vs météo officielle » sur la page du capteur, avec l'écart en couleur. |

**Terminé quand** : la page du capteur montre les deux valeurs côte à côte, et un écart fort est signalé.

---

## Bloc F — Sécurité

### J14 — Authentification (Firebase Authentication)

**Objectif** : seules les personnes autorisées peuvent voir le dashboard et agir.

| Couche | Tâches |
|--------|--------|
| Firebase | Activer **Authentication → E-mail/Mot de passe** dans la console. Créer 2 comptes : `admin` et `garde`. |
| Dashboard | Ajouter le SDK web Firebase. Page de connexion, bouton de déconnexion. Envoi du jeton (`Authorization: Bearer …`) à chaque appel API. |
| Serveur | Vérification du jeton avec `firebase_admin.auth.verify_id_token`. Routes protégées : écriture des fiches, commandes, traitement des alertes. Rôles : `admin` (tout) et `garde` (voir et traiter les alertes). Le champ `updated_by` des alertes (J10) est rempli. Les mesures de l'ESP32 (MQTT) ne sont pas concernées. |
| Bonus | Sécuriser MQTT avec un broker privé gratuit (HiveMQ Cloud) avec identifiant et mot de passe. |

**Terminé quand** : sans connexion, le dashboard affiche la page de connexion, et un compte `garde` ne peut pas envoyer de commandes.

---

## Bloc G — Intelligence artificielle

### J15 — Collecte et étiquetage de vraies données

**Objectif** : remplacer les données synthétiques par des mesures issues des simulations.

| Couche | Tâches |
|--------|--------|
| Serveur | Script `ml/export_firestore.py` : export des `measurements` vers un CSV. Étendre le simulateur avec les 5 capteurs et des scénarios variés (journée chaude, nuit humide, début de feu, feu avec vent, fausse alerte : fumée de barbecue sans chaleur…). Chaque mesure du simulateur porte son étiquette réelle (`label`). |
| Données | Viser au moins 2 000 mesures étiquetées, en équilibrant les 3 niveaux. |

**Terminé quand** : un fichier `ml/dataset_reel.csv` existe avec les 5 capteurs et l'étiquette.

### J16 — Nouveau modèle IA et comparaison

**Objectif** : un modèle sur 5 capteurs, évalué honnêtement.

| Couche | Tâches |
|--------|--------|
| Serveur | Adapter `train_model.py` aux 5 entrées. Comparer **règles seules / arbre de décision / Random Forest**, avec précision, rappel, matrice de confusion, faux positifs et faux négatifs. Montrer l'importance de chaque capteur (`feature_importances_`). Sauvegarder le meilleur modèle. Mettre à jour `risk.py` (5 entrées). |
| Rapport | Tableau comparatif et graphique de l'importance des capteurs. |

**Terminé quand** : le serveur utilise le nouveau modèle et `/api/health` indique `ai_model_loaded: true`.

---

## Bloc H — Finalisation

### J17 — Évaluation des scénarios

- Rejouer les 4 scénarios du sujet, plus les nouveaux : feu avec vent, capteur hors ligne, fausse alerte.
- Mesurer les faux positifs et faux négatifs, ainsi que le **délai capteur → alerte sur le dashboard → message Telegram**.
- Captures d'écran et courte vidéo de la démo.

### J18 — Rapport, slides, répétition

- Rapport : architecture, choix techniques, résultats de l'IA, évaluation, limites et perspectives.
- Slides (10 à 15).
- Répétition de la démo avec le chronomètre (moins de 10 min), et un plan B (le simulateur) si Wokwi ou le réseau ne marche pas.

---

## Règles de travail pour chaque jour

1. Partir de la dernière version : `git pull`.
2. Lancer le serveur et le dashboard, et vérifier que **tout marche avant** de modifier.
3. Faire les tâches du jour, couche par couche.
4. Tester avec le simulateur **et** Wokwi.
5. Lancer les tests : `cd server` puis `python -m pytest -q`.
6. Cocher le jour dans ce fichier (⬜ → ✅) et enregistrer sur GitHub (commit + push).
