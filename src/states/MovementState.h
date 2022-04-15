#ifndef MovementState_h
#define MovementState_h

#include <Arduino.h>
#include "eventdrivenstates/EventBus.h"
#include "events/MovementEvent.h"
#include "drivers/WheelsMotorDriver.h"

class MovementState : public State {
  protected:
    WheelsMotorDriver* wheelsMotorDriver;
  public:
    MovementState(WheelsMotorDriver* wheelsMotorDriver){
      this->wheelsMotorDriver = wheelsMotorDriver;
    }
    ~MovementState(){}
};

class StoppedState : public MovementState {
  public:
    State* transition(Event *event);
    StoppedState(WheelsMotorDriver* wheelsMotorDriver) : MovementState(wheelsMotorDriver){
      wheelsMotorDriver->stopMoving();
    }
    ~StoppedState(){}
};

class MoveForwardState : public MovementState {
  public:
    State* transition(Event *event);
    MoveForwardState(WheelsMotorDriver* wheelsMotorDriver) : MovementState(wheelsMotorDriver){
      wheelsMotorDriver->moveForward(255);
    }
    ~MoveForwardState(){}
};

State* StoppedState::transition(Event *event){
  MovementEvent *movementEvent = (MovementEvent*) event;
  if (strcmp(movementEvent->getEventKey(), MovementEvent::FORWARD)==0){
    return new MoveForwardState(this->wheelsMotorDriver);
  }
  return this;
}

State* MoveForwardState::transition(Event *event){
  MovementEvent *movementEvent = (MovementEvent*) event;
  if (strcmp(movementEvent->getEventKey(), MovementEvent::STOP)==0){
    return new StoppedState(this->wheelsMotorDriver);
  }
  return this;
}



#endif