# Configurer Firebase (Firestore)

Tant que Firebase n'est pas configuré, le serveur garde les données **en mémoire**
(elles sont perdues au redémarrage). Ces étapes activent le stockage permanent.

1. Aller sur <https://console.firebase.google.com> → **Ajouter un projet**
   (ex. `forestfireguard`). Google Analytics n'est pas nécessaire.
2. Menu **Build → Firestore Database → Créer une base de données**.
   Choisir une région proche (ex. `eur3` / `europe-west`) et le **mode production**.
   Le serveur passe par le SDK Admin : il n'est pas soumis aux règles de sécurité.
3. **Paramètres du projet (⚙️) → Comptes de service → Générer une nouvelle clé privée.**
   Un fichier JSON est téléchargé.
4. Renommer ce fichier `serviceAccountKey.json` et le placer dans `server/`.
   ⚠️ Il est déjà dans `.gitignore` : **ne jamais le commiter ni le partager**.
5. Dans `server/.env` : `USE_FIREBASE=true`, puis relancer le serveur.
6. Vérifier : `http://localhost:8000/api/health` doit afficher `"storage": "firebase (firestore)"`.
7. Envoyer quelques mesures (simulateur ou Wokwi), puis ouvrir la console Firestore :
   les collections `measurements` et `alerts` apparaissent.

## Index

La requête « mesures d'un capteur triées par date » (`/api/measurements?device_id=...`)
a besoin d'un index composite (`device_id` + `timestamp`). Au premier appel, Firestore renvoie
une erreur qui contient un **lien direct** pour créer cet index : il suffit de cliquer dessus.

## Structure des documents

`measurements` :
```json
{
  "device_id": "esp32-node-1",
  "temperature": 24.1, "humidity": 58.0, "smoke": 7.3,
  "timestamp": "2026-10-26T16:10:12.345+00:00",
  "risk": { "level": 0, "label": "faible", "source": "règles+ia", "reasons": [] }
}
```

`alerts` :
```json
{
  "device_id": "esp32-node-1", "timestamp": "...", "level": 2, "label": "élevé",
  "message": "Risque élevé : fumée très élevée (75 %)",
  "temperature": 47.4, "humidity": 17.4, "smoke": 75.0
}
```
