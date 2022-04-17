#ifndef GimbalEvent_h
#define GimbalEvent_h

#include "eventdrivenstates/EventBus.h"

class MoveGimbalEvent : public Event {
    private:
        int  horizontalAngle;
        int  verticalAngle;

    public:

        static constexpr const char* MOVE_GIMBAL = "gimbal.move";

        const char* getEventKey(){
            return MoveGimbalEvent::MOVE_GIMBAL;
        }

        MoveGimbalEvent(int horizontalAngle, int verticalAngle){
            this->horizontalAngle = horizontalAngle;
            this->verticalAngle = verticalAngle;
        }

        int getHorizontalAngle(){
            return this->horizontalAngle;
        }

        int getVerticalAngle(){
            return this->verticalAngle;
        }

};

#endif