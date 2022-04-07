#ifndef MovementControl_h
#define MovementControl_h

#include "eventbus/EventBus.h"

class MovementEvent : public Event {
    private:
        const char* eventId;

  public: 
    const char* getEventId(){
        return eventId;
    }

    MovementEvent(const char *eventId){
        this->eventId = eventId;
    }

    ~MovementEvent() {
    };

    Event* clone() {
        return new MovementEvent(this->eventId);
    }

};


#endif