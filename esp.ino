#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <DHT.h>

// ========== Настройки WiFi ==========
const char* ssid = "TP-Link_194B";
const char* password = "46488862";

// ========== Пины ==========
#define DHTPIN D2
#define DHTTYPE DHT11
#define SOIL_PIN A0
const int relayPins[4] = {D5, D6, D7, D8};

// ========== Объекты ==========
DHT dht(DHTPIN, DHTTYPE);
ESP8266WebServer server(80);

// ========== Данные ==========
float temperature = 0.0;
float humidity = 0.0;
int soilMoisture = 0;

// ========== Функции ==========
void setupWiFi() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  //WiFi.begin(ssid);
  
  Serial.println("Подключение к WiFi...");

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("\nWiFi подключен!");
  Serial.print("IP адрес: ");
  Serial.println(WiFi.localIP());
}

void readSensors() {
  humidity = dht.readHumidity();
  temperature = dht.readTemperature();
  
  int rawValue = analogRead(SOIL_PIN); // 0 (влажно) – 1023 (сухо)
  soilMoisture = map(rawValue, 1023, 0, 0, 100);  // 0% = сухо, 100% = влажно
  soilMoisture = constrain(soilMoisture, 0, 100); // Ограничение на границы
  
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Ошибка чтения DHT11");
  }
}

// Возвращает JSON с показаниями
void handleUpdateSensors() {
  readSensors();
  String jsonData = "{";
  jsonData += "\"temperature\": " + String(temperature, 1) + ",";
  jsonData += "\"humidity\": " + String(humidity, 1) + ",";
  jsonData += "\"soil_moisture\": " + String(soilMoisture);
  jsonData += "}";
  server.send(200, "application/json", jsonData);
}

// Управление реле
void handleRelayControl() {
  if (!server.hasArg("num") || !server.hasArg("state")) {
    server.send(400, "text/plain", "Missing parameters");
    return;
  }

  int relayNum = server.arg("num").toInt();
  String state = server.arg("state");

  if (relayNum < 1 || relayNum > 4) {
    server.send(400, "text/plain", "Invalid relay number");
    return;
  }

  int pin = relayPins[relayNum - 1];
  if (state == "on") {
    digitalWrite(pin, LOW);  // активный уровень зависит от модуля
  } else {
    digitalWrite(pin, HIGH);
  }

  server.send(200, "text/plain", "Relay updated");
}

void setup() {
  setupWiFi();
  dht.begin();

  // Настройка пинов реле
  for (int i = 0; i < 4; i++) {
    pinMode(relayPins[i], OUTPUT);
    digitalWrite(relayPins[i], HIGH);  // Выключаем реле по умолчанию
  }

  // Маршруты
  server.on("/update_sensors", HTTP_GET, handleUpdateSensors);
  server.on("/relay", HTTP_GET, handleRelayControl);

  server.begin();
  Serial.println("HTTP-сервер запущен.");
}

void loop() {
  server.handleClient();
}



