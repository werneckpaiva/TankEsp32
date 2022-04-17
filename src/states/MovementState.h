#ifndef MovementState_h
#define MovementState_h

#include <Arduino.h>
#include "eventdrivenstates/EventBus.h"
#include "events/MovementEvent.h"
#include "drivers/WheelsMotorDriver.h"
#include "eventdrivenstates/StatefulController.h"

class MovementState : public State {
  private:
    WheelsMotorDriver* wheelsMotorDriver;

  protected:
    int horizontalSpeed;
    int verticalSpeed;

    WheelsMotorDriver*  getWheelsMotorDriver(){
      return this->wheelsMotorDriver;
    }
    int getHorizontalSpeed(){
      return this->horizontalSpeed;
    }
    int getVerticalSpeed(){
      return this->verticalSpeed;
    }

  public:
    MovementState(EventBus *eventBus, WheelsMotorDriver* wheelsMotorDriver, int horizontalSpeed, int verticalSpeed) : State(eventBus){
      this->wheelsMotorDriver = wheelsMotorDriver;
      this->horizontalSpeed = horizontalSpeed;
      this->verticalSpeed = verticalSpeed;
    }
    ~MovementState(){}
};


// STATES #################################

class StoppedState : public MovementState {
  public:
    State* transition(Event *event);
    StoppedState(EventBus *eventBus, WheelsMotorDriver* wheelsMotorDriver) : MovementState(eventBus, wheelsMotorDriver, horizontalSpeed, verticalSpeed){
      wheelsMotorDriver->stopMoving();
    }
    ~StoppedState(){}
};

class MoveForwardState : public MovementState {
  public:
    State* transition(Event *event);
    MoveForwardState(EventBus *eventBus, WheelsMotorDriver* wheelsMotorDriver, int horizontalSpeed, int verticalSpeed) : MovementState(eventBus, wheelsMotorDriver, horizontalSpeed, verticalSpeed){
      wheelsMotorDriver->moveForward(horizontalSpeed, verticalSpeed);
    }
    ~MoveForwardState(){}
};

class MoveBackwardState : public MovementState {
  public:
    State* transition(Event *event);
    MoveBackwardState(EventBus *eventBus, WheelsMotorDriver* wheelsMotorDriver, int horizontalSpeed, int verticalSpeed) : MovementState(eventBus, wheelsMotorDriver, horizontalSpeed, verticalSpeed){
      wheelsMotorDriver->moveBackward(horizontalSpeed, verticalSpeed);
    }
    ~MoveBackwardState(){}
};

class SpinningRightState : public MovementState {
  public:
    State* transition(Event *event);
    SpinningRightState(EventBus *eventBus, WheelsMotorDriver* wheelsMotorDriver, int speed) : MovementState(eventBus, wheelsMotorDriver, speed, 0){
      wheelsMotorDriver->spinRight(speed);
    }
    ~SpinningRightState(){}
};

class SpinningLeftState : public MovementState {
  public:
    State* transition(Event *event);
    SpinningLeftState(EventBus *eventBus, WheelsMotorDriver* wheelsMotorDriver, int speed) : MovementState(eventBus, wheelsMotorDriver, speed, 0){
      wheelsMotorDriver->spinLeft(speed);
    }
    ~SpinningLeftState(){}
};

// Transitions  #################################

State* StoppedState::transition(Event *event){
  if (strcmp(event->getEventKey(), MovementEvent::FORWARD)==0){
    MovementForwardEvent *movementEvent = (MovementForwardEvent*) event;
    return new MoveForwardState(this->getEventBus(), this->getWheelsMotorDriver(), movementEvent->getHorizontalSpeed(), movementEvent->getVerticalSpeed());

  } else if (strcmp(event->getEventKey(), MovementEvent::BACKWARD)==0){
    MovementBackwardEvent *movementEvent = (MovementBackwardEvent*) event;
    return new MoveBackwardState(this->getEventBus(), this->getWheelsMotorDriver(), movementEvent->getHorizontalSpeed(), movementEvent->getVerticalSpeed());

  } else if (strcmp(event->getEventKey(), MovementEvent::SPIN_RIGHT)==0){
    MovementSpinRightEvent *movementEvent = (MovementSpinRightEvent*) event;
    return new SpinningRightState(this->getEventBus(), this->getWheelsMotorDriver(), movementEvent->getHorizontalSpeed());

  } else if (strcmp(event->getEventKey(), MovementEvent::SPIN_LEFT)==0){
    MovementSpinLeftEvent *movementEvent = (MovementSpinLeftEvent*) event;
    return new SpinningLeftState(this->getEventBus(), this->getWheelsMotorDriver(), movementEvent->getHorizontalSpeed());
  }
  return this;
}

State* MoveForwardState::transition(Event *event){
  if (strcmp(event->getEventKey(), MovementEvent::STOP)==0 ||
      strcmp(event->getEventKey(), MovementEvent::BACKWARD)==0){
    return new StoppedState(this->getEventBus(), this->getWheelsMotorDriver());

  } else if (strcmp(event->getEventKey(), MovementEvent::FORWARD)==0){
    MovementForwardEvent *movementEvent = (MovementForwardEvent*) event;
    return new MoveForwardState(this->getEventBus(), this->getWheelsMotorDriver(), movementEvent->getHorizontalSpeed(), movementEvent->getVerticalSpeed());
  }
  return this;
}

State* MoveBackwardState::transition(Event *event){
  if (strcmp(event->getEventKey(), MovementEvent::STOP)==0 ||
      strcmp(event->getEventKey(), MovementEvent::FORWARD)==0){
    return new StoppedState(this->getEventBus(), this->getWheelsMotorDriver());
  
  } else if (strcmp(event->getEventKey(), MovementEvent::BACKWARD)==0){
    MovementBackwardEvent *movementEvent = (MovementBackwardEvent*) event;
    return new MoveBackwardState(this->getEventBus(), this->getWheelsMotorDriver(), movementEvent->getHorizontalSpeed(), movementEvent->getVerticalSpeed());
  }
  return this;
}

State* SpinningRightState::transition(Event *event){
  if (strcmp(event->getEventKey(), MovementEvent::STOP) == 0 ||
      strcmp(event->getEventKey(), MovementEvent::SPIN_LEFT) == 0){
    return new StoppedState(this->getEventBus(), this->getWheelsMotorDriver());

  } else if (strcmp(event->getEventKey(), MovementEvent::SPIN_RIGHT)==0){
    MovementSpinRightEvent *movementEvent = (MovementSpinRightEvent*) event;
    return new SpinningRightState(this->getEventBus(), this->getWheelsMotorDriver(), movementEvent->getHorizontalSpeed());
  }
  return this;
}

State* SpinningLeftState::transition(Event *event){
  if (strcmp(event->getEventKey(), MovementEvent::STOP)==0 ||
      strcmp(event->getEventKey(), MovementEvent::SPIN_RIGHT) == 0){
    return new StoppedState(this->getEventBus(), this->getWheelsMotorDriver());
  } else if (strcmp(event->getEventKey(), MovementEvent::SPIN_LEFT)==0){
    MovementSpinLeftEvent *spinEvent = (MovementSpinLeftEvent*) event;    
    // if (abs(spinEvent->getHorizontalSpeed() - this->getHorizontalSpeed()) > 5){
    return new SpinningLeftState(this->getEventBus(), this->getWheelsMotorDriver(), spinEvent->getHorizontalSpeed());
    // }
  }
  return this;
}




#endif