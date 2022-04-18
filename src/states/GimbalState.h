#ifndef GimbalState_h
#define GimbalState_h

#include <Arduino.h>
#include "eventdrivenstates/EventBus.h"
#include "eventdrivenstates/StatefulController.h"
#include "events/GimbalEvent.h"
#include "drivers/GimbalDriver.h"


class ManualControlState : public State {
    private:
        GimbalDriver *gimbalDriver;
        int  horizontalAngle;
        int  verticalAngle;

    protected:
        GimbalDriver *getGimbalDriver(){
            return this->gimbalDriver;
        }

    public:
        ManualControlState(EventBus *eventBus, GimbalDriver *gimbalDriver, int horizontalAngle = 90, int verticalAngle = 90) : State(eventBus){
            this->gimbalDriver = gimbalDriver;
            this->horizontalAngle = horizontalAngle;
            this->verticalAngle = verticalAngle;

            this->moveGimbal(horizontalAngle, verticalAngle);
        }
        State* transition(Event *event);
        void moveGimbal( int horizontalAngle, int verticalAngle);
};

State* ManualControlState::transition(Event *event){
    if (strcmp(event->getEventKey(), MoveGimbalEvent::MOVE_GIMBAL)==0){
        MoveGimbalEvent *gimbalEvent = (MoveGimbalEvent*) event;
        if (abs(this->horizontalAngle - gimbalEvent->getHorizontalAngle()) > 2
            || abs(this->verticalAngle - gimbalEvent->getVerticalAngle()) > 2){
            return new ManualControlState(
                this->getEventBus(),
                this->gimbalDriver,
                gimbalEvent->getHorizontalAngle(),
                gimbalEvent->getVerticalAngle());
        }
    }
    return this;
}

void ManualControlState::moveGimbal( int horizontalAngle, int verticalAngle){
    int sanitizedHorizontalAngle = map(horizontalAngle, 0, 180, 20, 160);
    int sanitizedVerticalAngle = map(verticalAngle, 0, 180, 20, 160);
    gimbalDriver->pan(sanitizedHorizontalAngle);
    gimbalDriver->tilt(sanitizedVerticalAngle);
}


#endif