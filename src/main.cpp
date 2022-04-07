#include <Arduino.h>

#include "eventbus/EventBus.h"
#include "movement/MovementEvent.h"
#include "controller/StatefulController.h"



EventBus *eventBus;
StatefulController *statefulController1;
StatefulController *statefulController2;


void iterateEvent(void *params){
  for(;;){
    MovementEvent *event1 = new MovementEvent("movement.stop");
    // MovementEvent *event2 = new MovementEvent("movement.start");
    // MovementEvent *event3 = new MovementEvent("movement.turn.left");
    // MovementEvent *event4 = new MovementEvent("movement.turn.right");
    eventBus->dispatchEvent(event1);
    // eventBus->dispatchEvent(event2);
    // eventBus->dispatchEvent(event3);
    // eventBus->dispatchEvent(event4);

  
    Serial.printf("\nHeap: %d bytes\n", ESP.getFreeHeap());
     vTaskDelay(100 / portTICK_PERIOD_MS);
  }
}

class StoppedState : public State{
    State* transition(Event *event){
      Serial.printf("Transition event: %s\s\n", event->getEventKey());
      return this;
    }
    ~StoppedState(){

    }
};

void setup() {
  Serial.begin(115200);
  eventBus = new EventBus(10);
  statefulController1 = new StatefulController(new StoppedState());
  statefulController2 = new StatefulController(new StoppedState());
  eventBus->addEventListener("movement", statefulController1);
  eventBus->addEventListener("movement.turn", statefulController2);


  xTaskCreate(iterateEvent,
                "t1",
                10 * 1024,
                NULL,
                20,
                NULL);

}

void loop() { }
