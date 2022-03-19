#include <Arduino.h>

#include "EventBus.h"

void setup() {
  Serial.begin(115200);
  EventBus::init(10);
}


void loop() {

}
