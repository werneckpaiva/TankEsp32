#ifndef MovementState_h
#define MovementState_h

#include <Arduino.h>
#include "eventdrivenstates/EventBus.h"
#include "eventdrivenstates/StatefulController.h"
#include "states/MovementState.h"
#include "events/MovementEvent.h"

class StoppedState : public State{
    State* transition(Event *event){
      MovementEvent *movementEvent = (MovementEvent*) event;
      Serial.printf("Transition event: %s / speed: %d\n", movementEvent->getEventKey(), movementEvent->getSpeed());
      return this;
    }
    ~StoppedState(){

    }
};

#endif