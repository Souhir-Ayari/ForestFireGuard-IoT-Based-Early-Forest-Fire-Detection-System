# Guide de lancement pas à pas (Windows)

Pas besoin de PlatformIO pour ce guide. Il suffit de faire les étapes dans l'ordre.

## Étape 0 — À installer une seule fois

1. **Python** : <https://www.python.org/downloads/>
   ⚠️ Pendant l'installation, cocher **« Add python.exe to PATH »**.
2. **Node.js** (version **LTS**) : <https://nodejs.org>
3. Télécharger le projet : sur GitHub, bouton vert **Code → Download ZIP**, puis dézipper
   (ou `git clone ...` si tu utilises Git).

## Étape 1 — Lancer le serveur

Dans le dossier du projet, **double-cliquer sur `1_lancer_serveur.bat`**.

- La première fois, l'installation prend quelques minutes.
- Quand c'est prêt, la fenêtre affiche `Uvicorn running on http://127.0.0.1:8000`.
- Vérifier dans le navigateur : <http://localhost:8000/docs>.
- **Laisser la fenêtre ouverte** : si on la ferme, le serveur s'arrête.

## Étape 2 — Lancer le dashboard

**Double-cliquer sur `2_lancer_dashboard.bat`.**

- La première fois, l'installation prend quelques minutes.
- Le navigateur s'ouvre sur <http://localhost:5173>.
- **Laisser cette fenêtre ouverte aussi.**

## Étape 3 — Envoyer des données

Choisir **A** ou **B**.

### A. Le simulateur (le plus simple, idéal pour la démo)

**Double-cliquer sur `3_lancer_simulateur.bat`.**
Sur le dashboard, le risque passe de **faible** (vert) à **modéré** (jaune), puis à **élevé** (rouge),
et des alertes apparaissent.

### B. L'ESP32 dans Wokwi (sur le site, sans rien installer)

1. Aller sur <https://wokwi.com>, se connecter, puis cliquer sur **New Project → ESP32**.
2. Remplacer le contenu de l'onglet **`sketch.ino`** par celui du fichier `iot/wokwi/sketch.ino`.
3. Remplacer le contenu de l'onglet **`diagram.json`** par celui du fichier `iot/wokwi/diagram.json`.
4. Ajouter les bibliothèques. Dans l'onglet **Library Manager**, ajouter :
   `DHT sensor library for ESPx`, `PubSubClient` et `ArduinoJson`.
5. Cliquer sur le bouton vert **▶**. En bas, le moniteur série affiche `Connexion WiFi... OK`,
   puis `Connexion MQTT... OK`, puis `Envoi -> {...}` toutes les 2 secondes.
6. Les mesures apparaissent sur le dashboard (capteur `esp32-node-1`).
7. Pour tester, cliquer pendant la simulation sur le **DHT22** (température, humidité),
   sur le **capteur de gaz** (fumée) ou sur le **capteur de flamme**.

> Le serveur (étape 1) doit tourner, sinon les LEDs restent pilotées par les règles locales
> de l'ESP32, et rien n'arrive sur le dashboard.

## En cas de problème

| Problème | Solution |
|---|---|
| `'python' n'est pas reconnu` | Réinstaller Python en cochant **Add python.exe to PATH** |
| `'npm' n'est pas reconnu` | Installer Node.js LTS, puis redémarrer le PC |
| Dashboard : « Serveur injoignable » | L'étape 1 n'est pas lancée, ou sa fenêtre a été fermée |
| Dashboard : pastille « MQTT ✗ » | Le réseau bloque le port 1883 (Wi-Fi de l'école ?) : essayer en partage de connexion depuis le téléphone. Le simulateur (A) marche quand même. |
| Wokwi n'envoie rien au dashboard | Vérifier que `TOPIC_BASE` dans `sketch.ino` est identique à `MQTT_TOPIC_BASE` dans `server/.env` |

## Et PlatformIO ?

PlatformIO sert **uniquement** si tu veux lancer Wokwi **dans VS Code** au lieu du site wokwi.com.
C'est optionnel : la méthode B ci-dessus fait la même chose sans rien installer.
Les explications sont dans le `README.md`, section « Wokwi dans VS Code ».
