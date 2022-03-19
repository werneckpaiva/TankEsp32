#include <Arduino.h>

#include <ESP32Servo.h>
#include <IBusBM.h>

Servo servoHorz; 
Servo servoVert; 
IBusBM ibusRc;

#define LED_PORT 14
const int servoHorzPin = 25;
const int servoVertPin = 26;

HardwareSerial& ibusRcSerial = Serial2;

void setup() {
  Serial.begin(115200);
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);

  servoHorz.setPeriodHertz(50);
  servoHorz.attach(servoHorzPin, 500, 2400);

  servoVert.setPeriodHertz(50);
  servoVert.attach(servoVertPin, 500, 2400);

  ibusRc.begin(ibusRcSerial, 1);

  pinMode(LED_PORT, OUTPUT);
}

int readChannel(byte channelInput, int minLimit, int maxLimit, int defaultValue){
  uint16_t ch = ibusRc.readChannel(channelInput);
  if (ch < 100) return defaultValue;
  int value = map(ch, 1000, 2000, minLimit, maxLimit);
  if (value < minLimit) return minLimit;
  if (value > maxLimit) return maxLimit;
  return value;
}

// Red the channel and return a boolean value
bool redSwitch(byte channelInput, bool defaultValue){
  int intDefaultValue = (defaultValue)? 100: 0;
  int ch = readChannel(channelInput, 0, 100, intDefaultValue);
  return (ch > 50);
}

void blinkLed(int duration) {
//  for (int i = 0; i < 5; i++) {
    digitalWrite(LED_PORT, HIGH);
    delay(duration);
    digitalWrite(LED_PORT, LOW);
    delay(duration);  
//  }
}

int prevHorzValue=90;
int prevVertValue=90;

int ledOn = HIGH;

void loop() {
  int horzValue = readChannel(0, 20, 160, 90);
  horzValue = 180 - horzValue;
  if (abs(prevHorzValue - horzValue) > 2){
    servoHorz.write(horzValue);  
    prevHorzValue = horzValue;
  }
  int vertValue = readChannel(1, 20, 160, 90);
  if (abs(prevVertValue - vertValue) > 2){
    servoVert.write(vertValue);  
    prevVertValue = vertValue;
  }
  Serial.print(horzValue);
  Serial.print(" ");
  Serial.println(vertValue);
  delay(20);
}
