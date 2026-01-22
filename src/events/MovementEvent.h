#ifndef MovementEvent_h
#define MovementEvent_h

#include <EventDrivenStates.h>

class MovementEvent : public Event {
    private:
        const char* eventKey;

  public:
    static constexpr const char* STOP = "movement.stop";
    static constexpr const char* FORWARD = "movement.forward";
    static constexpr const char* BACKWARD = "movement.backward";
    static constexpr const char* SPIN_RIGHT = "movement.spin.right";
    static constexpr const char* SPIN_LEFT = "movement.spin.left";

    virtual const char* getEventKey(){
        return eventKey;
    }

    MovementEvent(const char *eventKey){
        this->eventKey = eventKey;
    }

    virtual ~MovementEvent() {};
    virtual Event* clone() const = 0;

};

class MovementStopEvent : public MovementEvent {
    public:
        MovementStopEvent() : MovementEvent(MovementEvent::STOP){}
        Event* clone() const override { return new MovementStopEvent(*this); }
};

class MovementWithSpeedEvent : public MovementEvent {
    private:
        int horizontalSpeed;
        int verticalSpeed;
    public:
        MovementWithSpeedEvent(const char *eventKey, int horizontalSpeed, int verticalSpeed) : MovementEvent(eventKey){
            this->horizontalSpeed = horizontalSpeed;
            this->verticalSpeed = verticalSpeed;
        }
        int getHorizontalSpeed(){
            return this->horizontalSpeed;
        }
        int getVerticalSpeed(){
            return this->verticalSpeed;
        }
        virtual Event* clone() const = 0;
};

class MovementForwardEvent : public MovementWithSpeedEvent {
    public:
        MovementForwardEvent(int horizontalSpeed, int verticalSpeed) : MovementWithSpeedEvent(MovementEvent::FORWARD, horizontalSpeed, verticalSpeed){}
        Event* clone() const override { return new MovementForwardEvent(*this); }
};

class MovementBackwardEvent : public MovementWithSpeedEvent {
    public:
        MovementBackwardEvent(int horizontalSpeed, int verticalSpeed) : MovementWithSpeedEvent(MovementEvent::BACKWARD, horizontalSpeed, verticalSpeed){}
        Event* clone() const override { return new MovementBackwardEvent(*this); }
};

class MovementSpinRightEvent : public MovementWithSpeedEvent {
    public:
        MovementSpinRightEvent(int speed) : MovementWithSpeedEvent(MovementEvent::SPIN_RIGHT, speed, 0){}
        Event* clone() const override { return new MovementSpinRightEvent(*this); }
};

class MovementSpinLeftEvent : public MovementWithSpeedEvent {
    public:
        MovementSpinLeftEvent(int speed) : MovementWithSpeedEvent(MovementEvent::SPIN_LEFT, speed, 0){}
        Event* clone() const override { return new MovementSpinLeftEvent(*this); }
};



#endif