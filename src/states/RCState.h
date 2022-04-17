#ifndef RCState_h
#define RCState_h

#include <Arduino.h>
#include "eventdrivenstates/EventBus.h"
#include "eventdrivenstates/StatefulController.h"
#include "events/MovementEvent.h"
#include "events/GimbalEvent.h"
#include "drivers/RCDriver.h"

class RCMonitoringState : public State {
  protected:
    RCDriver *rcDriver;
    static const unsigned int SAMPLING_INTERVAL_MS = 50;
    static const int SPEED_THRESHOLD = 10;

  public:
    RCMonitoringState(EventBus *eventBus, RCDriver* rcDriver);
    State* transition(Event *event);
    static void readRC(void *params);
    void processMovement(int horizontalSpeed, int verticalSpeed);
    void processGimbal(int horizontalAngle, int verticalAngle);
    ~RCMonitoringState(){}
};

RCMonitoringState::RCMonitoringState(EventBus *eventBus, RCDriver* rcDriver) : State(eventBus){
      this->rcDriver = rcDriver;
      xTaskCreate(RCMonitoringState::readRC,
                "readRC",
                5 * 1024,
                (void *) this,
                20,
                NULL);
}

State* RCMonitoringState::transition(Event *event){
    return this;
}

void RCMonitoringState::readRC(void *params){
    RCMonitoringState *self = (RCMonitoringState*) params;
     for(;;){
        int horizontalSpeed = self->rcDriver->readChannel(0, -255, 255, 0);
        int verticalSpeed = self->rcDriver->readChannel(1, -255, 255, 0);
        self->processMovement(horizontalSpeed, verticalSpeed);

        int verticalAngle = self->rcDriver->readChannel(2, 0, 180, 90);
        int horizontalAngle = self->rcDriver->readChannel(3, 180, 0, 90);
        self->processGimbal(horizontalAngle, verticalAngle);

        vTaskDelay(RCMonitoringState::SAMPLING_INTERVAL_MS / portTICK_PERIOD_MS);
    }
}

void RCMonitoringState::processMovement(int horizontalSpeed, int verticalSpeed){
    if (verticalSpeed > SPEED_THRESHOLD){
        this->getEventBus()->dispatchEvent(new MovementForwardEvent(horizontalSpeed, verticalSpeed));
    } else if (verticalSpeed < -SPEED_THRESHOLD){
        this->getEventBus()->dispatchEvent(new MovementBackwardEvent(horizontalSpeed, verticalSpeed));
    } else if (horizontalSpeed > SPEED_THRESHOLD){
        this->getEventBus()->dispatchEvent(new MovementSpinRightEvent(horizontalSpeed));
    } else if (horizontalSpeed < -SPEED_THRESHOLD){
        this->getEventBus()->dispatchEvent(new MovementSpinLeftEvent(horizontalSpeed));
    } else {
        this->getEventBus()->dispatchEvent(new MovementStopEvent());
    }
}

void RCMonitoringState::processGimbal(int horizontalAngle, int verticalAngle){
    this->getEventBus()->dispatchEvent(new MoveGimbalEvent(horizontalAngle, verticalAngle));
}

#endif