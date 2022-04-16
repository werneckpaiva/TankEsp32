#ifndef RCState_h
#define RCState_h

#include <Arduino.h>
#include "eventdrivenstates/EventBus.h"
#include "eventdrivenstates/StatefulController.h"
#include "events/MovementEvent.h"
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
    void processMovement(int horizSpeed, int vertSpeed);
    ~RCMonitoringState(){}
};

RCMonitoringState::RCMonitoringState(EventBus *eventBus, RCDriver* rcDriver) : State(eventBus){
      this->rcDriver = rcDriver;
      xTaskCreatePinnedToCore(RCMonitoringState::readRC,
                "readRC",
                5 * 1024,
                (void *) this,
                20,
                NULL,
                1);
}

State* RCMonitoringState::transition(Event *event){
    return this;
}

void RCMonitoringState::readRC(void *params){
    RCMonitoringState *self = (RCMonitoringState*) params;
     for(;;){
        int horizSpeed = self->rcDriver->readChannel(0, -255, 255, 0);
        int vertSpeed = self->rcDriver->readChannel(1, -255, 255, 0);
        self->processMovement(horizSpeed, vertSpeed);
        vTaskDelay(RCMonitoringState::SAMPLING_INTERVAL_MS / portTICK_PERIOD_MS);
    }
}

void RCMonitoringState::processMovement(int horizSpeed, int vertSpeed){
    if (vertSpeed > SPEED_THRESHOLD){
        this->getEventBus()->dispatchEvent(new MovementForwardEvent(horizSpeed, vertSpeed));
    } else if (vertSpeed < -SPEED_THRESHOLD){
        this->getEventBus()->dispatchEvent(new MovementBackwardEvent(horizSpeed, vertSpeed));
    } else if (horizSpeed > SPEED_THRESHOLD){
        this->getEventBus()->dispatchEvent(new MovementSpinRightEvent(horizSpeed));
    } else if (horizSpeed < -SPEED_THRESHOLD){
        this->getEventBus()->dispatchEvent(new MovementSpinLeftEvent(horizSpeed));
    } else {
        this->getEventBus()->dispatchEvent(new MovementStopEvent());
    }
}

#endif