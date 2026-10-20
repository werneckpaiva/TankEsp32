#ifndef GimbalState_h
#define GimbalState_h

#include <Arduino.h>
#include <EventDrivenStates.h>
#include "events/GimbalEvent.h"
#include "drivers/GimbalDriver.h"


/*
 * Follows the RC gimbal stick. Its constructor moves the servos.
 */
class ManualControlState : public State {
    private:
        static const int MAX_ANGLE = 180;
        static const int CENTER_ANGLE = 90;
        // Requested angles 0..MAX_ANGLE are scaled into this servo range
        static const int SERVO_MIN_ANGLE = 20;
        static const int SERVO_MAX_ANGLE = 160;
        // Smaller angle changes than this keep the servos where they are
        static const int MIN_ANGLE_CHANGE = 2;

        GimbalDriver *gimbalDriver;
        int  horizontalAngle;
        int  verticalAngle;

    protected:
        GimbalDriver *getGimbalDriver(){
            return this->gimbalDriver;
        }

    public:
        ManualControlState(EventBus *eventBus, GimbalDriver *gimbalDriver, int horizontalAngle = CENTER_ANGLE, int verticalAngle = CENTER_ANGLE) : State(eventBus){
            this->gimbalDriver = gimbalDriver;
            this->horizontalAngle = horizontalAngle;
            this->verticalAngle = verticalAngle;

            this->moveGimbal(horizontalAngle, verticalAngle);
        }
        State* transition(Event *event);
        void moveGimbal( int horizontalAngle, int verticalAngle);
};

State* ManualControlState::transition(Event *event){
    if (event->is(MoveGimbalEvent::MOVE_GIMBAL)){
        MoveGimbalEvent *gimbalEvent = (MoveGimbalEvent*) event;
        if (abs(this->horizontalAngle - gimbalEvent->getHorizontalAngle()) > MIN_ANGLE_CHANGE
            || abs(this->verticalAngle - gimbalEvent->getVerticalAngle()) > MIN_ANGLE_CHANGE){
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
    int panServoAngle = map(horizontalAngle, 0, MAX_ANGLE, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE);
    int tiltServoAngle = map(verticalAngle, 0, MAX_ANGLE, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE);
    gimbalDriver->pan(panServoAngle);
    gimbalDriver->tilt(tiltServoAngle);
}

#endif