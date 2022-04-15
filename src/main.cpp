#include <Arduino.h>

#include "eventdrivenstates/EventBus.h"
#include "eventdrivenstates/StatefulController.h"
#include "events/MovementEvent.h"
#include "states/MovementState.h"

// Pins
const byte motor1aPin = 18;
const byte motor1bPin = 19;
const byte motor2aPin = 22;
const byte motor2bPin = 23;

const byte rcSerialPin = 16;


EventBus *eventBus;
StatefulController *movementController;
WheelsMotorDriver *wheelsMotorDriver;

void generateEvents(void *params){
  bool isMoving = false;
  Event *event;
  for(;;){
    if (isMoving){
      event = new MovementEvent(MovementEvent::FORWARD);
    } else {
      event = new MovementEvent(MovementEvent::STOP);
    }
    isMoving = !isMoving;
    eventBus->dispatchEvent(event);
    Serial.printf("\nHeap: %d bytes\n", ESP.getFreeHeap());
    vTaskDelay(1000 / portTICK_PERIOD_MS);
  }
}

void setup() {
  Serial.begin(115200);

  eventBus = new EventBus(10);
  wheelsMotorDriver = new WheelsMotorDriver(motor1aPin, motor1bPin, motor2aPin, motor2bPin);
  movementController = new StatefulController(new StoppedState(wheelsMotorDriver));
  eventBus->addEventListener("movement", movementController);

  xTaskCreate(generateEvents,
                "generateEvents",
                10 * 1024,
                NULL,
                20,
                NULL);

}

void loop() { }
