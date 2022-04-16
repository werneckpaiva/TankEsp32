#ifndef MovementEvent_h
#define MovementEvent_h

#include "eventdrivenstates/EventBus.h"

class MovementEvent : public Event {
    private:
        const char* eventKey;

  public:
    static constexpr const char* STOP = "movement.stop";
    static constexpr const char* FORWARD = "movement.forward";
    static constexpr const char* BACKWARD = "movement.backward";
    static constexpr const char* SPIN_RIGHT = "movement.spin.right";
    static constexpr const char* SPIN_LEFT = "movement.spin.left";

    const char* getEventKey(){
        return eventKey;
    }

    MovementEvent(const char *eventKey){
        this->eventKey = eventKey;
    }

    ~MovementEvent() {
    };

    Event* clone() {
        return new MovementEvent(this->eventKey);
    }

};

class MovementStopEvent : public MovementEvent {
    public:
        MovementStopEvent() : MovementEvent(MovementEvent::STOP){}
};

class MovementWithSpeed : public MovementEvent {
    private:
        int horizontalSpeed;
        int verticalSpeed;
    public:
        MovementWithSpeed(const char *eventKey, int horizontalSpeed, int verticalSpeed) : MovementEvent(eventKey){
            this->horizontalSpeed = horizontalSpeed;
            this->verticalSpeed = verticalSpeed;
        }
        int getHorizontalSpeed(){
            return this->horizontalSpeed;
        }
        int getVerticalSpeed(){
            return this->verticalSpeed;
        }
};

class MovementForwardEvent : public MovementWithSpeed {
    public:
        MovementForwardEvent(int horizontalSpeed, int verticalSpeed) : MovementWithSpeed(MovementEvent::FORWARD, horizontalSpeed, verticalSpeed){}
};

class MovementBackwardEvent : public MovementWithSpeed {
    public:
        MovementBackwardEvent(int horizontalSpeed, int verticalSpeed) : MovementWithSpeed(MovementEvent::BACKWARD, horizontalSpeed, verticalSpeed){}
};

class MovementSpinRightEvent : public MovementWithSpeed {
    public:
        MovementSpinRightEvent(int speed) : MovementWithSpeed(MovementEvent::SPIN_RIGHT, speed, 0){}
};

class MovementSpinLeftEvent : public MovementWithSpeed {
    public:
        MovementSpinLeftEvent(int speed) : MovementWithSpeed(MovementEvent::SPIN_LEFT, speed, 0){}
};



#endif