#ifndef MovementEvent_h
#define MovementEvent_h

#include "eventdrivenstates/EventBus.h"

class MovementEvent : public Event {
    private:
        const char* eventKey;
        int speed = 10;

  public: 
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

    int getSpeed(){
        return this->speed;
    }

};


#endif