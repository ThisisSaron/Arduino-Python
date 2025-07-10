// Use Arduino Mega or Mega 2560

// LED, fan, window

#include <EEPROM.h>
#include <Servo.h>

#define LEDPIN 13 // eeprom 0, key A
#define FANPIN 6 // eeprom 1, key B

int ledState = LOW;
int fanState = HIGH;
Servo servo_10;
Servo servo_9;


void setup() {
  Serial.begin(115200);

  // LED setup
  pinMode(LEDPIN, OUTPUT);
  ledState = EEPROM.read(0);
  digitalWrite(LEDPIN, ledState);

  // Fan setup
  pinMode(FANPIN, OUTPUT);
  fanState = EEPROM.read(1);
  digitalWrite(FANPIN, fanState);

  // Window setup
  servo_9.attach(9);
  servo_10.attach(10);
  servo_9.write(0);
  servo_10.write(0);
}

void loop() {
  if (Serial.available()) {
    String x = Serial.readStringUntil('\n');
    if (x == "A0") {
      digitalWrite(LEDPIN, 0);
      ledState = 0;
      Serial.println("LED off");
    } else if (x == "A1") {
      digitalWrite(LEDPIN, 1);
      ledState = 1;
      Serial.println("LED on");
    } else if (x == "B0") {
      digitalWrite(FANPIN, 1);
      fanState = 1;
      Serial.println("Fan off");
    } else if (x == "B1") {
      digitalWrite(FANPIN, 0);
      fanState = 0;
      Serial.println("Fan on");
    } else if (x == "C0") {
      servo_9.write(0);
      servo_10.write(0);
      Serial.println("Window open");
      delay(5000);
    } else if (x == "C1") {
      servo_9.write(180);
      servo_10.write(180);
      Serial.println("Window closed");
      delay(5000);
    } else {
      Serial.println("Incorrect format");
    }
  }
  EEPROM.write(0, ledState);
  EEPROM.write(1, fanState);
}


