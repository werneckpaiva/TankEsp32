#ifndef StatefulController_h
#define StatefulController_h

#include <Arduino.h>
#include "eventbus/EventBus.h"

// Driver
// SatefulController
// - EventListener
//   - Task

class State{
    public:
        virtual State* transition(Event *event);
        virtual ~State(){}
};

class StatefulController : public EventListener {
  private:
    State *currentState;
  public:
    void receiveEvent(Event *event);
};


void StatefulController::receiveEvent(Event *event){
        State *oldState = this->currentState;
        this->currentState = this->currentState->transition(event);
        if (oldState != this->currentState){
            delete(oldState);
        }
        Serial.printf("StatefulController: event received: %s (proc: %d)\n", event->getEventId(), xPortGetCoreID());
    }

#endif