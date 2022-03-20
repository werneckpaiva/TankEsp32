#include <Arduino.h>

#include "EventBus.h"
#include "MovementControl.h"


class MovementEventListener : public EventListener {
  public:
    void receiveEvent(EventBase *event){
      Serial.printf("MovementEventListener: event received: %d (proc: %d)\n", event->eventType(), xPortGetCoreID());
    }
};

MovementEventListener movementEventListener1;
MovementEventListener movementEventListener2;

void setup() {
  Serial.begin(115200);
  EventBus::init(10);
  EventBus::addEventListener(&movementEventListener1);
  EventBus::addEventListener(&movementEventListener2);
  
}

void loop() {

  MovementEvent *event = new MovementEvent(MovementEvent::MOVE_STOP);
  EventBus::dispatchEvent(event);
  
  Serial.printf("\nHeap: %d bytes\n", ESP.getFreeHeap());

  delay(1000);
}
