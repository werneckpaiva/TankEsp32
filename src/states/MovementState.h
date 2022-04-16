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
    MovementState(EventBus *eventBus, WheelsMotorDriver* wheelsMotorDriver) : State(eventBus){
      this->wheelsMotorDriver = wheelsMotorDriver;
    }
    ~MovementState(){}
};


// STATES #################################

class StoppedState : public MovementState {
  public:
    State* transition(Event *event);
    StoppedState(EventBus *eventBus, WheelsMotorDriver* wheelsMotorDriver) : MovementState(eventBus, wheelsMotorDriver){
      wheelsMotorDriver->stopMoving();
    }
    ~StoppedState(){}
};

class MoveForwardState : public MovementState {
  public:
    State* transition(Event *event);
    MoveForwardState(EventBus *eventBus, WheelsMotorDriver* wheelsMotorDriver, int horizontalSpeed, int verticalSpeed) : MovementState(eventBus, wheelsMotorDriver){
      wheelsMotorDriver->moveForward(horizontalSpeed, verticalSpeed);
    }
    ~MoveForwardState(){}
};

class MoveBackwardState : public MovementState {
  public:
    State* transition(Event *event);
    MoveBackwardState(EventBus *eventBus, WheelsMotorDriver* wheelsMotorDriver, int horizontalSpeed, int verticalSpeed) : MovementState(eventBus, wheelsMotorDriver){
      wheelsMotorDriver->moveBackward(horizontalSpeed, verticalSpeed);
    }
    ~MoveBackwardState(){}
};

class SpinningRightState : public MovementState {
  public:
    State* transition(Event *event);
    SpinningRightState(EventBus *eventBus, WheelsMotorDriver* wheelsMotorDriver, int speed) : MovementState(eventBus, wheelsMotorDriver){
      wheelsMotorDriver->spinRight(speed);
    }
    ~SpinningRightState(){}
};

class SpinningLeftState : public MovementState {
  public:
    State* transition(Event *event);
    SpinningLeftState(EventBus *eventBus, WheelsMotorDriver* wheelsMotorDriver, int speed) : MovementState(eventBus, wheelsMotorDriver){
      wheelsMotorDriver->spinLeft(speed);
    }
    ~SpinningLeftState(){}
};

// Transitions  #################################

State* StoppedState::transition(Event *event){
  if (strcmp(event->getEventKey(), MovementEvent::FORWARD)==0){
    MovementForwardEvent *movementEvent = (MovementForwardEvent*) event;
    return new MoveForwardState(this->getEventBus(), this->wheelsMotorDriver, movementEvent->getHorizontalSpeed(), movementEvent->getVerticalSpeed());

  } else if (strcmp(event->getEventKey(), MovementEvent::BACKWARD)==0){
    MovementBackwardEvent *movementEvent = (MovementBackwardEvent*) event;
    return new MoveBackwardState(this->getEventBus(), this->wheelsMotorDriver, movementEvent->getHorizontalSpeed(), movementEvent->getVerticalSpeed());

  } else if (strcmp(event->getEventKey(), MovementEvent::SPIN_RIGHT)==0){
    MovementSpinRightEvent *movementEvent = (MovementSpinRightEvent*) event;
    return new SpinningRightState(this->getEventBus(), this->wheelsMotorDriver, movementEvent->getHorizontalSpeed());

  } else if (strcmp(event->getEventKey(), MovementEvent::SPIN_LEFT)==0){
    MovementSpinLeftEvent *movementEvent = (MovementSpinLeftEvent*) event;
    return new SpinningLeftState(this->getEventBus(), this->wheelsMotorDriver, movementEvent->getHorizontalSpeed());
  }
  return this;
}

State* MoveForwardState::transition(Event *event){
  MovementEvent *movementEvent = (MovementEvent*) event;
  if (strcmp(movementEvent->getEventKey(), MovementEvent::STOP)==0 ||
      strcmp(movementEvent->getEventKey(), MovementEvent::BACKWARD)==0){
    return new StoppedState(this->getEventBus(), this->wheelsMotorDriver);

  } else if (strcmp(movementEvent->getEventKey(), MovementEvent::FORWARD)==0){
    MovementForwardEvent *movementEvent = (MovementForwardEvent*) event;
    return new MoveForwardState(this->getEventBus(), this->wheelsMotorDriver, movementEvent->getHorizontalSpeed(), movementEvent->getVerticalSpeed());
  }
  return this;
}

State* MoveBackwardState::transition(Event *event){
  MovementEvent *movementEvent = (MovementEvent*) event;
  if (strcmp(movementEvent->getEventKey(), MovementEvent::STOP)==0 ||
      strcmp(movementEvent->getEventKey(), MovementEvent::FORWARD)==0){
    return new StoppedState(this->getEventBus(), this->wheelsMotorDriver);
  
  } else if (strcmp(movementEvent->getEventKey(), MovementEvent::BACKWARD)==0){
    MovementBackwardEvent *movementEvent = (MovementBackwardEvent*) event;
    return new MoveBackwardState(this->getEventBus(), this->wheelsMotorDriver, movementEvent->getHorizontalSpeed(), movementEvent->getVerticalSpeed());
  }
  return this;
}

State* SpinningRightState::transition(Event *event){
  MovementEvent *movementEvent = (MovementEvent*) event;
  if (strcmp(movementEvent->getEventKey(), MovementEvent::STOP)==0 ||
      strcmp(movementEvent->getEventKey(), MovementEvent::SPIN_LEFT)){
    return new StoppedState(this->getEventBus(), this->wheelsMotorDriver);

  } else if (strcmp(movementEvent->getEventKey(), MovementEvent::SPIN_RIGHT)==0){
    MovementBackwardEvent *movementEvent = (MovementBackwardEvent*) event;
    return new SpinningRightState(this->getEventBus(), this->wheelsMotorDriver, movementEvent->getHorizontalSpeed());
  }
  return this;
}

State* SpinningLeftState::transition(Event *event){
  MovementEvent *movementEvent = (MovementEvent*) event;
  if (strcmp(movementEvent->getEventKey(), MovementEvent::STOP)==0 ||
      strcmp(movementEvent->getEventKey(), MovementEvent::SPIN_RIGHT)){
    return new StoppedState(this->getEventBus(), this->wheelsMotorDriver);
  } else if (strcmp(movementEvent->getEventKey(), MovementEvent::SPIN_LEFT)==0){
    MovementBackwardEvent *movementEvent = (MovementBackwardEvent*) event;
    return new SpinningLeftState(this->getEventBus(), this->wheelsMotorDriver, movementEvent->getHorizontalSpeed());
  }
  return this;
}




#endif