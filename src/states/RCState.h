#ifndef RCState_h
#define RCState_h

#include <Arduino.h>
#include <EventDrivenStates.h>
#include "events/MovementEvent.h"
#include "events/GimbalEvent.h"
#include "events/LightEvent.h"
#include "drivers/RCDriver.h"

class RCMonitoringState : public State {
  protected:
    RCDriver *rcDriver;
    static const unsigned int SAMPLING_INTERVAL_MS = 50;
    static const int SPEED_THRESHOLD = 10;

  public:
    int ch0 = 0;
    int ch1 = 0;
    int ch2 = 0;
    int ch3 = 0;
    bool ch4 = false;

    RCMonitoringState(EventBus *eventBus, RCDriver* rcDriver);
    State* transition(Event *event);
    static void readRC(void *params);
    void processChannels(int ch0, int ch1, int ch2, int ch3, bool ch4);
    void processMovement(int horizontalSpeed, int verticalSpeed);
    void processGimbal(int horizontalAngle, int verticalAngle);
    void processLight(bool lightsOn);
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
        int ch0 = self->rcDriver->readChannel(0, -255, 255, 0);
        int ch1 = self->rcDriver->readChannel(1, -255, 255, 0);
        int ch2 = self->rcDriver->readChannel(2, 180, 0, 90);
        int ch3 = self->rcDriver->readChannel(3, 180, 0, 90);
        bool ch4 = self->rcDriver->redSwitch(4, false);

        self->processChannels(ch0, ch1, ch2, ch3, ch4);

        vTaskDelay(RCMonitoringState::SAMPLING_INTERVAL_MS / portTICK_PERIOD_MS);
    }
}

void RCMonitoringState::processChannels(int ch0, int ch1, int ch2, int ch3, bool ch4){
    Serial.println(ch4);
    if (ch0 != this->ch0 || ch1 != this->ch1){
        this->ch0 = ch0;
        this->ch1 = ch1;
        this->processMovement(ch0, ch1);
    }
    if (ch2 != this->ch2 || ch3 != this->ch3){
        this->ch2 = ch2;
        this->ch3 = ch3;
        this->processGimbal(ch3, ch2);
    }
    if (ch4 != this->ch4){
        this->ch4 = ch4;
        this->processLight(ch4);
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

void RCMonitoringState::processLight(bool lightsOn){
    if (lightsOn){
        this->getEventBus()->dispatchEvent(new TurnFrontLightOnEvent());
    } else {
        this->getEventBus()->dispatchEvent(new TurnFrontLightOffEvent());
    }
}

#endif