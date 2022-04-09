#include <Arduino.h>

#include "eventdrivenstates/EventBus.h"
#include "eventdrivenstates/StatefulController.h"
#include "events/MovementEvent.h"
#include "states/MovementState.h"

EventBus *eventBus;
StatefulController *movementController;


void generateEvents(void *params){
  const char* eventIds[] = {"movement.stop", "movement.start", "movement.turn.left", "movement.turn.right"};
  for(;;){
    eventBus->dispatchEvent(new MovementEvent(eventIds[random(4)]));
    Serial.printf("\nHeap: %d bytes\n", ESP.getFreeHeap());
    vTaskDelay(100 / portTICK_PERIOD_MS);
  }
}

void setup() {
  Serial.begin(115200);

  eventBus = new EventBus(10);
  movementController = new StatefulController(new StoppedState());
  eventBus->addEventListener("movement", movementController);

  xTaskCreate(generateEvents,
                "generateEvents",
                10 * 1024,
                NULL,
                20,
                NULL);

}

void loop() { }
