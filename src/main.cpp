#include <Arduino.h>

#include "drivers/RCDriver.h"
#include "drivers/WheelsMotorDriver.h"
#include "drivers/GimbalDriver.h"
#include "drivers/LightsStripDriver.h"

#include "events/MovementEvent.h"

#include "states/MovementState.h"
#include "states/RCState.h" 
#include "states/GimbalState.h"
#include "states/FrontLighstState.h"

#include <EventDrivenStates.h>


// Pins
const byte motor1aPin = 18;
const byte motor1bPin = 19;
const byte motor2aPin = 22;
const byte motor2bPin = 23;

const byte gimbalHorizontalPin = 25;
const byte gimbalVerticalPin = 26;

const byte frontLedStripPin = 21;

const byte distanceEchoPin = 35;
const byte distanceTriggerPin = 32;

EventBus *eventBus;

WheelsMotorDriver *wheelsMotorDriver;
RCDriver *rcDriver;
GimbalDriver *gimbalDriver;
LightsStripDriver *lightsDriver;


StatefulController *movementController;
StatefulController *rcController;
StatefulController *gimbalController;
StatefulController *frontLightsController;

void printStatus(void *params){
  for(;;){
    Serial.printf("\nHeap: %d bytes\n", ESP.getFreeHeap());
    vTaskDelay(2000 / portTICK_PERIOD_MS);
  }
}

void setup() {
  Serial.begin(115200);

  eventBus              = new EventBus(10);

  wheelsMotorDriver     = new WheelsMotorDriver(motor1aPin, motor1bPin, motor2aPin, motor2bPin);
  rcDriver              = new RCDriver(Serial2);
  gimbalDriver          = new GimbalDriver(gimbalHorizontalPin, gimbalVerticalPin);
  lightsDriver          = new LightsStripDriver(8, frontLedStripPin);

  movementController    = new StatefulController(new StoppedState(eventBus, wheelsMotorDriver));
  rcController          = new StatefulController(new RCMonitoringState(eventBus, rcDriver));
  gimbalController      = new StatefulController(new ManualControlState(eventBus, gimbalDriver));  
  frontLightsController = new StatefulController(new FrontLightOffState(eventBus, lightsDriver));

  eventBus->addEventListener("movement.", movementController);
  eventBus->addEventListener("gimbal.", gimbalController);
  eventBus->addEventListener("", frontLightsController);



  xTaskCreate(printStatus,
                "printStatus",
                5 * 1024,
                NULL,
                20,
                NULL);

}

void loop() { }
