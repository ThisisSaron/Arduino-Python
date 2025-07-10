// Use ESP32 Dev Module

// LED, fan, window

#include <EEPROM.h>
#include <ESP32Servo.h>

#define LEDPIN 12 // eeprom 0, key A
#define FANPIN 19 // eeprom 1, key B
#define SERVOPIN 5

int ledState = LOW;
int fanState = LOW;
Servo servo_5;


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
  servo_5.setPeriodHertz(50);
  servo_5.attach(SERVOPIN, 1000, 2000);
  delay(200);
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
      digitalWrite(FANPIN, 0);
      fanState = 1;
      Serial.println("Fan off");
    } else if (x == "B1") {
      digitalWrite(FANPIN, 1);
      fanState = 0;
      Serial.println("Fan on");
    } else if (x == "C0") {
      servo_5.write(0);
      Serial.println("Window open");
      delay(5000);
    } else if (x == "C1") {
      servo_5.write(180);
      Serial.println("Window closed");
      delay(5000);
    } else {
      Serial.println("Incorrect format");
    }
  }
  EEPROM.write(0, ledState);
  EEPROM.write(1, fanState);
}



// Window open/close
/*
#include <Servo.h>

Servo servo_10;
Servo servo_9;

void setup() {
  Serial.begin(115200);
  servo_9.attach(9);
  servo_10.attach(10);
  servo_9.write(0);
  servo_10.write(0);
}

void loop() {
  if (Serial.available()) {
    String x = Serial.readStringUntil('\n');
    if (x == "0") {
      servo_9.write(0);
      servo_10.write(0);
      Serial.println("Window open");
      delay(5000);
    } else if (x == "1") {
      servo_9.write(180);
      servo_10.write(180);
      Serial.println("Window closed");
      delay(5000);
    }
  }
}


// Sings Happy Birthday
void setup() {
  Serial.begin(115200);
}

void loop() {
  if (Serial.available()) {
    String x = Serial.readStringUntil('\n');
    if (x == "0") {
      noTone(3);
      Serial.println("Tone stopped");
    } else if (x == "1") {
      Serial.println("Tone started");
      tone(3, 294); //digital 3 outputs 294HZ sound 
      delay(250);//delay in 250ms
      tone(3, 440);
      delay(250);
      tone(3, 392);
      delay(250);
      tone(3, 532);
      delay(250);
      tone(3, 494);
      delay(500);
      tone(3, 392);
      delay(250);
      tone(3, 440);
      delay(250);
      tone(3, 392);
      delay(250);
      tone(3, 587);
      delay(250);
      tone(3, 532);
      delay(500);
      tone(3, 392);
      delay(250);
      tone(3, 784);
      delay(250);
      tone(3, 659);
      delay(250);
      tone(3, 532);
      delay(250);
      tone(3, 494);
      delay(250);
      tone(3, 440);
      delay(250);
      tone(3, 698);
      delay(375);
      tone(3, 659);
      delay(250);
      tone(3, 532);
      delay(250);
      tone(3, 587);
      delay(250);
      tone(3, 532);
      delay(500);
      noTone(3);
    }
  }
}

*/