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

    // Transmitter channel assignment
    static const byte TURN_CHANNEL = 0;
    static const byte THROTTLE_CHANNEL = 1;
    static const byte TILT_CHANNEL = 2;
    static const byte PAN_CHANNEL = 3;
    static const byte LIGHTS_SWITCH_CHANNEL = 4;

    static const int MAX_SPEED = 255;
    static const int MAX_ANGLE = 180;
    static const int CENTER_ANGLE = 90;

    // Last values read; events are only dispatched when they change
    int turnSpeed = 0;
    int throttleSpeed = 0;
    int tiltAngle = 0;
    int panAngle = 0;
    bool lightsOn = false;

  public:
    RCMonitoringState(EventBus *eventBus, RCDriver* rcDriver);
    State* transition(Event *event);
    static void readRC(void *params);
    void processChannels(int turnSpeed, int throttleSpeed, int tiltAngle, int panAngle, bool lightsOn);
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
        int turnSpeed = self->rcDriver->readChannel(TURN_CHANNEL, -MAX_SPEED, MAX_SPEED, 0);
        int throttleSpeed = self->rcDriver->readChannel(THROTTLE_CHANNEL, -MAX_SPEED, MAX_SPEED, 0);
        // Gimbal channels are mapped inverted: the lowest pulse gives MAX_ANGLE
        int tiltAngle = self->rcDriver->readChannel(TILT_CHANNEL, MAX_ANGLE, 0, CENTER_ANGLE);
        int panAngle = self->rcDriver->readChannel(PAN_CHANNEL, MAX_ANGLE, 0, CENTER_ANGLE);
        bool lightsOn = self->rcDriver->readSwitch(LIGHTS_SWITCH_CHANNEL, false);
        self->processChannels(turnSpeed, throttleSpeed, tiltAngle, panAngle, lightsOn);
        vTaskDelay(RCMonitoringState::SAMPLING_INTERVAL_MS / portTICK_PERIOD_MS);
    }
}

void RCMonitoringState::processChannels(int turnSpeed, int throttleSpeed, int tiltAngle, int panAngle, bool lightsOn){
    if (turnSpeed != this->turnSpeed || throttleSpeed != this->throttleSpeed){
        this->turnSpeed = turnSpeed;
        this->throttleSpeed = throttleSpeed;
        this->processMovement(turnSpeed, throttleSpeed);
    }
    if (tiltAngle != this->tiltAngle || panAngle != this->panAngle){
        this->tiltAngle = tiltAngle;
        this->panAngle = panAngle;
        this->processGimbal(panAngle, tiltAngle);
    }
    if (lightsOn != this->lightsOn){
        this->lightsOn = lightsOn;
        this->processLight(lightsOn);
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