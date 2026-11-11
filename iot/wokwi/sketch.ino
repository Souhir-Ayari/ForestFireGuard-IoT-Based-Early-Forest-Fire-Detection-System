/*
 * ForestFireGuard — Nœud capteur ESP32 (simulation Wokwi)
 *
 * Capteurs : DHT22 (température / humidité) + MQ-2 (gaz / fumée) + capteur de flamme infrarouge
 * Actionneurs : LED verte / jaune / rouge + buzzer
 * Communication : MQTT (broker public) -> serveur FastAPI local
 *
 * Toutes les 2 s, l'ESP32 publie une mesure JSON sur  <TOPIC_BASE>/<DEVICE_ID>/data
 * et écoute le niveau de risque renvoyé par le serveur sur <TOPIC_BASE>/<DEVICE_ID>/risk.
 * Si le serveur ne répond pas, des règles locales prennent le relais.
 */
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "DHTesp.h"

// ---------- Configuration ----------
const char* WIFI_SSID   = "Wokwi-GUEST";
const char* WIFI_PASS   = "";
const char* MQTT_BROKER = "broker.hivemq.com";
const int   MQTT_PORT   = 1883;
// Doit correspondre à MQTT_TOPIC_BASE dans server/.env
const char* TOPIC_BASE  = "forestfireguard/souhir-ayari";
const char* DEVICE_ID   = "esp32-node-1";

const unsigned long SEND_INTERVAL_MS  = 2000;
const unsigned long SERVER_TIMEOUT_MS = 10000;  // au-delà : règles locales

// ---------- Broches ----------
const int DHT_PIN    = 15;
const int SMOKE_PIN  = 34;  // MQ-2 : sortie analogique AOUT (ADC1)
const int FLAME_PIN  = 32;  // capteur de flamme : sortie numérique DOUT
// La sortie DOUT du capteur de flamme passe à LOW quand une flamme est détectée.
// Si "flame" vaut true sans flamme dans Wokwi, mettre false ici.
const bool FLAME_ACTIVE_LOW = true;
const int LED_GREEN  = 25;
const int LED_YELLOW = 26;
const int LED_RED    = 27;
const int BUZZER_PIN = 14;

DHTesp dht;
WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);

char topicData[96];
char topicRisk[96];

int serverLevel = -1;
unsigned long lastServerReply = 0;
unsigned long lastSend = 0;

// Règles de secours, identiques à celles du serveur (server/app/risk.py)
int localRiskLevel(float t, float h, float smoke, bool flame) {
  if (flame || smoke >= 60 || (t >= 50 && h <= 20)) return 2;
  if (smoke >= 30 || (t >= 35 && h <= 30) || t >= 50) return 1;
  return 0;
}

void showLevel(int level) {
  digitalWrite(LED_GREEN,  level == 0);
  digitalWrite(LED_YELLOW, level == 1);
  digitalWrite(LED_RED,    level == 2);
  if (level == 2) tone(BUZZER_PIN, 1000);
  else noTone(BUZZER_PIN);
}

void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  JsonDocument doc;
  if (deserializeJson(doc, payload, length)) return;
  serverLevel = doc["level"] | -1;
  lastServerReply = millis();
  Serial.printf("Serveur -> risque %s (%d)\n", (const char*)(doc["label"] | "?"), serverLevel);
}

void connectWiFi() {
  Serial.print("Connexion WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASS, 6);
  while (WiFi.status() != WL_CONNECTED) {
    delay(250);
    Serial.print(".");
  }
  Serial.println(" OK");
}

void connectMqtt() {
  while (!mqtt.connected()) {
    String clientId = String("ffg-") + DEVICE_ID + "-" + String(random(0xffff), HEX);
    Serial.print("Connexion MQTT... ");
    if (mqtt.connect(clientId.c_str())) {
      mqtt.subscribe(topicRisk);
      Serial.println("OK");
    } else {
      Serial.printf("échec (%d), nouvel essai\n", mqtt.state());
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(FLAME_PIN, INPUT);
  dht.setup(DHT_PIN, DHTesp::DHT22);

  snprintf(topicData, sizeof(topicData), "%s/%s/data", TOPIC_BASE, DEVICE_ID);
  snprintf(topicRisk, sizeof(topicRisk), "%s/%s/risk", TOPIC_BASE, DEVICE_ID);

  connectWiFi();
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  mqtt.setCallback(onMqttMessage);
  connectMqtt();
}

void loop() {
  if (!mqtt.connected()) connectMqtt();
  mqtt.loop();

  if (millis() - lastSend < SEND_INTERVAL_MS) return;
  lastSend = millis();

  TempAndHumidity th = dht.getTempAndHumidity();
  if (dht.getStatus() != DHTesp::ERROR_NONE) {
    Serial.println("Erreur de lecture DHT22");
    return;
  }
  float smoke = analogRead(SMOKE_PIN) * 100.0 / 4095.0;  // 0-4095 -> 0-100 %
  bool flame = digitalRead(FLAME_PIN) == (FLAME_ACTIVE_LOW ? LOW : HIGH);

  JsonDocument doc;
  doc["device_id"]   = DEVICE_ID;
  doc["temperature"] = round(th.temperature * 10) / 10.0;
  doc["humidity"]    = round(th.humidity * 10) / 10.0;
  doc["smoke"]       = round(smoke * 10) / 10.0;
  doc["flame"]       = flame;
  char buffer[160];
  serializeJson(doc, buffer);
  mqtt.publish(topicData, buffer);
  Serial.printf("Envoi -> %s\n", buffer);

  bool serverOk = serverLevel >= 0 && millis() - lastServerReply < SERVER_TIMEOUT_MS;
  showLevel(serverOk ? serverLevel : localRiskLevel(th.temperature, th.humidity, smoke, flame));
}
