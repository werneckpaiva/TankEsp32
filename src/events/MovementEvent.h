#ifndef MovementEvent_h
#define MovementEvent_h

#include "eventdrivenstates/EventBus.h"

class MovementEvent : public Event {
    private:
        const char* eventKey;

  public:
    static constexpr const char* FORWARD = "movement.forward";
    static constexpr const char* STOP = "movement.stop";

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


#endif