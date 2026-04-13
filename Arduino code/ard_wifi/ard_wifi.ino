#include <WiFi.h>
#include <EEPROM.h>
#include <ESP32Servo.h>

// Wi-Fi credentials
const char* ssid = "AUITS";
const char* password = "";

// Pins
#define LEDPIN 12
#define FANPIN 19
#define SERVOPIN 5

// Device states
int ledState = LOW;
int fanState = LOW;
Servo servo_5;

// TCP Server on port 8888
WiFiServer server(8888);

void setup() {
  Serial.begin(115200);
  EEPROM.begin(10);  // Reserve EEPROM space

  // Setup pins
  pinMode(LEDPIN, OUTPUT);
  pinMode(FANPIN, OUTPUT);

  // Restore states from EEPROM
  ledState = EEPROM.read(0);
  fanState = EEPROM.read(1);
  digitalWrite(LEDPIN, ledState);
  digitalWrite(FANPIN, fanState);

  // Setup servo
  servo_5.setPeriodHertz(50);
  servo_5.attach(SERVOPIN, 1000, 2000);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  server.begin(); // Start TCP server
}

void handleCommand(String cmd) {
  cmd.trim();
  if (cmd == "A0") {
    digitalWrite(LEDPIN, LOW);
    ledState = LOW;
    Serial.println("LED off");
  } else if (cmd == "A1") {
    digitalWrite(LEDPIN, HIGH);
    ledState = HIGH;
    Serial.println("LED on");
  } else if (cmd == "B0") {
    digitalWrite(FANPIN, LOW);
    fanState = LOW;
    Serial.println("Fan off");
  } else if (cmd == "B1") {
    digitalWrite(FANPIN, HIGH);
    fanState = HIGH;
    Serial.println("Fan on");
  } else if (cmd == "C0") {
    servo_5.write(0);
    Serial.println("Window open");
    delay(5000);
  } else if (cmd == "C1") {
    servo_5.write(180);
    Serial.println("Window closed");
    delay(5000);
  } else {
    Serial.println("Invalid command: " + cmd);
  }

  // Save states
  EEPROM.write(0, ledState);
  EEPROM.write(1, fanState);
  EEPROM.commit();
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Client connected");

    while (client.connected()) {
      if (client.available()) {
        String cmd = client.readStringUntil('\n');
        Serial.println("Received: " + cmd);
        handleCommand(cmd);
        client.println("OK");  // Send back response
      }
    }

    client.stop();
    Serial.println("Client disconnected");
  }
}
