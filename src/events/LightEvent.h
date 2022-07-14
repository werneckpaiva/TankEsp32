#ifndef LightEvent_h
#define LightEvent_h

#include <EventDrivenStates.h>

class LightEvent : public Event{
    private:
        const char* eventKey;
    public:
        static constexpr const char* LIGHT_FRONT_ON = "light.front.on";
        static constexpr const char* LIGHT_FRONT_OFF = "light.front.off";

        LightEvent(const char *eventKey){
            this->eventKey = eventKey;
        }

        const char* getEventKey(){
            return this->eventKey;
        }

        ~LightEvent() {}
};

class TurnFrontLightOnEvent : public LightEvent {
  public:
    TurnFrontLightOnEvent() : LightEvent(LightEvent::LIGHT_FRONT_ON){}
};

class TurnFrontLightOffEvent : public LightEvent {
  public:
    TurnFrontLightOffEvent() : LightEvent(LightEvent::LIGHT_FRONT_OFF){}
};

#endif