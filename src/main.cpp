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

const byte frontLedStripPin = 27;

const byte distanceEchoPin = 35;
const byte distanceTriggerPin = 32;

EventBus *eventBus;

WheelsMotorDriver *wheelsMotorDriver;
RCDriver *rcDriver;
GimbalDriver *gimbalDriver;
LightsStripDriver *lightsDriver;


// Event source only: its readRC task publishes RC input to the bus
RCMonitoringState *rcMonitor;

StatefulController *movementController;
StatefulController *gimbalController;
StatefulController *frontLightsController;

#ifdef DEBUG_MODE
// Only exists in debug builds: periodically logs heap and listener stack usage
void printStatus(void *params){
  for(;;){
    DEBUG_PRINTF("Heap: %d bytes, Max Alloc: %d bytes, Min Free: %d bytes\n", ESP.getFreeHeap(), ESP.getMaxAllocHeap(), ESP.getMinFreeHeap());
    DEBUG_PRINTF("Listener min free stack: movement %u, gimbal %u, lights %u bytes\n",
                  movementController->getStackHighWaterMark(), gimbalController->getStackHighWaterMark(),
                  frontLightsController->getStackHighWaterMark());
    vTaskDelay(2000 / portTICK_PERIOD_MS);
  }
}
#endif

void setup() {
  Serial.begin(115200);

  eventBus              = new EventBus(10);

  wheelsMotorDriver     = new WheelsMotorDriver(motor1aPin, motor1bPin, motor2aPin, motor2bPin);
  rcDriver              = new RCDriver(Serial2);
  gimbalDriver          = new GimbalDriver(gimbalHorizontalPin, gimbalVerticalPin);
  lightsDriver          = new LightsStripDriver(8, frontLedStripPin);

  movementController    = new StatefulController(new StoppedState(eventBus, wheelsMotorDriver));
  rcMonitor             = new RCMonitoringState(eventBus, rcDriver);
  gimbalController      = new StatefulController(new ManualControlState(eventBus, gimbalDriver));  
  frontLightsController = new StatefulController(new FrontLightOffState(eventBus, lightsDriver));

  eventBus->addEventListener("movement.", movementController);
  eventBus->addEventListener("gimbal.", gimbalController);
  eventBus->addEventListener("", frontLightsController);


  DEBUG_PRINTLN("Setup done");
#ifdef DEBUG_MODE
  xTaskCreate(printStatus,
                "printStatus",
                5 * 1024,
                NULL,
                20,
                NULL);
#endif

}

void loop() {delay(1);}
