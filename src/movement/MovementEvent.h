#ifndef MovementControl_h
#define MovementControl_h

#include "eventbus/EventBus.h"

class MovementEvent : public Event {
    private:
        const char* eventKey;

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

};


#endif