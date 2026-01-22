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

        virtual const char* getEventKey(){
            return this->eventKey;
        }

        virtual ~LightEvent() {}
        virtual Event* clone() const = 0;
};

class TurnFrontLightOnEvent : public LightEvent {
  public:
    TurnFrontLightOnEvent() : LightEvent(LightEvent::LIGHT_FRONT_ON){}
    Event* clone() const override { return new TurnFrontLightOnEvent(*this); }
};

class TurnFrontLightOffEvent : public LightEvent {
  public:
    TurnFrontLightOffEvent() : LightEvent(LightEvent::LIGHT_FRONT_OFF){}
    Event* clone() const override { return new TurnFrontLightOffEvent(*this); }
};

#endif