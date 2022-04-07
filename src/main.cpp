#include <Arduino.h>

#include "eventbus/EventBus.h"
#include "movement/MovementEvent.h"
#include "controller/StatefulController.h"



EventBus *eventBus;
StatefulController statefulController1;
StatefulController statefulController2;

void setup() {
  Serial.begin(115200);
  eventBus = new EventBus(10);
  eventBus->addEventListener(&statefulController1);
  eventBus->addEventListener(&statefulController2);
}

void loop() {

  MovementEvent *event1 = new MovementEvent("movement.stop");
  MovementEvent *event2 = new MovementEvent("movement.start");
  MovementEvent *event3 = new MovementEvent("movement.turnleft");
  MovementEvent *event4 = new MovementEvent("movement.turnright");
  eventBus->dispatchEvent(event1);
  eventBus->dispatchEvent(event2);
  eventBus->dispatchEvent(event3);
  eventBus->dispatchEvent(event4);

  
  Serial.printf("\nHeap: %d bytes\n", ESP.getFreeHeap());

  delay(1000);
}
