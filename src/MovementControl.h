#ifndef MovementControl_h
#define MovementControl_h

#include "EventBus.h"

class MovementEvent : public EventBase {
  public: 
   enum MovementType {
      MOVE_STOP,                // 0
      MOVE_FORWARD,             // 1
      MOVE_BACKWARD,            // 2
      MOVE_LEFT,                // 3
      MOVE_RIGHT,               // 4
    };

    int eventType(){
        return 0;
    }

    MovementEvent(MovementType movement);

    int movementType();

    protected:
        virtual ~MovementEvent() = default;

  private:
    int movement;

};

MovementEvent::MovementEvent(MovementType movement){
    this->movement = movement;
}


int MovementEvent::movementType(){
    return this->movement;

}


#endif