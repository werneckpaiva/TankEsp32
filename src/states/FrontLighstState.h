#ifndef FrontLightsState_h
#define FrontLightsState_h

#include <Arduino.h>
#include "drivers/LightsStripDriver.h"
#include "events/LightEvent.h"


class LightState : public State {
private:
  LightsStripDriver *lightsStripDriver;

public:
  LightState(EventBus *eventBus, LightsStripDriver *lightsStripDriver) : State(eventBus) {
    this->lightsStripDriver = lightsStripDriver;
  }

  LightsStripDriver *getLightsStripDriver() { return this->lightsStripDriver; }

  virtual ~LightState() {}
};

// STATES #################################

/*
 * Waiting to turn it on
 */
class FrontLightOffState : public LightState {
public:
  FrontLightOffState(EventBus *eventBus, LightsStripDriver *lightsStripDriver) : LightState(eventBus, lightsStripDriver) {
    lightsStripDriver->clear();
  }
  State *transition(Event *event);
};

/*
 * Waiting for something to happen
 */
class FrontLightRestingState : public LightState {
public:
  FrontLightRestingState(EventBus *eventBus, LightsStripDriver *lightsStripDriver) : LightState(eventBus, lightsStripDriver) {
    lightsStripDriver->fullPaint(LightsStripDriver::BLUE(), 1);
  }
  State *transition(Event *event);
};

class FrontLightMovingState : public LightState {
  static constexpr const float MAX_BRIGHTNESS = 0.7;

public:
  FrontLightMovingState(EventBus *eventBus, LightsStripDriver *lightsStripDriver, int speed, const byte *color) : LightState(eventBus, lightsStripDriver) {
    float brightness = abs((speed / 255.0) * MAX_BRIGHTNESS);
    lightsStripDriver->fullPaint(color, brightness);
  }
  State *transition(Event *event);
};

class FrontLightMovingForwardState : public FrontLightMovingState {
public:
  FrontLightMovingForwardState(EventBus *eventBus, LightsStripDriver *lightsStripDriver, int speed) : FrontLightMovingState(eventBus, lightsStripDriver, speed, LightsStripDriver::GREEN()) {

  }
};

class FrontLightMovingBackwardState : public FrontLightMovingState {
public:
  FrontLightMovingBackwardState(EventBus *eventBus,
                                LightsStripDriver *lightsStripDriver, int speed)
      : FrontLightMovingState(eventBus, lightsStripDriver, speed,
                              LightsStripDriver::RED()) {}
};

class FrontLightRestingMovingGimbalState : public LightState {
private:
  int horizontalAngle;

public:
  static constexpr const float LEFT_LIGHT_ANGLE = 80.0;
  static constexpr const float RIGHT_LIGHT_ANGLE = 100.0;
  static constexpr const float NUM_PIXELS_ON = 8;
  static constexpr const float NUM_ALWAYS_PIXELS_ON = 2;
  static constexpr const float MAX_BRIGHTNESS = .5;
  FrontLightRestingMovingGimbalState(EventBus *eventBus,
                                     LightsStripDriver *lightsStripDriver,
                                     int horizontalAngle)
      : LightState(eventBus, lightsStripDriver) {
    this->horizontalAngle = horizontalAngle;
    this->showLights(horizontalAngle);
  }
  void showLights(int horizontalAngle);
  State *transition(Event *event);
};

// Transitions  #################################

State *FrontLightOffState::transition(Event *event) {
  if (strcmp(event->getEventKey(), LightEvent::LIGHT_FRONT_ON) == 0) {
    State* newState = new FrontLightRestingState(this->getEventBus(), this->getLightsStripDriver());
    Serial.printf("New state address: %p\n", newState);
    return newState;
  }
  return this;
}

State *FrontLightRestingState::transition(Event *event) {
  if (strcmp(event->getEventKey(), MovementEvent::FORWARD) == 0) {
    MovementWithSpeedEvent *movementEvent = (MovementWithSpeedEvent *)event;
    return new FrontLightMovingForwardState(this->getEventBus(),
                                            this->getLightsStripDriver(),
                                            movementEvent->getVerticalSpeed());
  } else if (strcmp(event->getEventKey(), MovementEvent::BACKWARD) == 0) {
    MovementWithSpeedEvent *movementEvent = (MovementWithSpeedEvent *)event;
    return new FrontLightMovingBackwardState(this->getEventBus(),
                                             this->getLightsStripDriver(),
                                             movementEvent->getVerticalSpeed());
  } else if (strcmp(event->getEventKey(), MoveGimbalEvent::MOVE_GIMBAL) == 0) {
    MoveGimbalEvent *gimbalEvent = (MoveGimbalEvent *)event;
    return new FrontLightRestingMovingGimbalState(
        this->getEventBus(), this->getLightsStripDriver(),
        gimbalEvent->getHorizontalAngle());
  } else if (strcmp(event->getEventKey(), LightEvent::LIGHT_FRONT_OFF) == 0) {
    return new FrontLightOffState(this->getEventBus(),
                                  this->getLightsStripDriver());
  }
  return this;
}

State *FrontLightMovingState::transition(Event *event) {
  if (strcmp(event->getEventKey(), MovementEvent::STOP) == 0) {
    return new FrontLightRestingState(this->getEventBus(),
                                      this->getLightsStripDriver());
  } else if (strcmp(event->getEventKey(), MovementEvent::FORWARD) == 0) {
    MovementWithSpeedEvent *movementEvent = (MovementWithSpeedEvent *)event;
    return new FrontLightMovingForwardState(this->getEventBus(),
                                            this->getLightsStripDriver(),
                                            movementEvent->getVerticalSpeed());
  } else if (strcmp(event->getEventKey(), MovementEvent::BACKWARD) == 0) {
    MovementWithSpeedEvent *movementEvent = (MovementWithSpeedEvent *)event;
    return new FrontLightMovingBackwardState(this->getEventBus(),
                                             this->getLightsStripDriver(),
                                             movementEvent->getVerticalSpeed());
  } else if (strcmp(event->getEventKey(), LightEvent::LIGHT_FRONT_OFF) == 0) {
    return new FrontLightOffState(this->getEventBus(),
                                  this->getLightsStripDriver());
  }
  return this;
}

State *FrontLightRestingMovingGimbalState::transition(Event *event) {
  if (strcmp(event->getEventKey(), MoveGimbalEvent::MOVE_GIMBAL) == 0) {
    MoveGimbalEvent *movementEvent = (MoveGimbalEvent *)event;
    if (movementEvent->getHorizontalAngle() < 80 ||
        movementEvent->getHorizontalAngle() > 100) {
      if (abs(this->horizontalAngle - movementEvent->getHorizontalAngle()) >
          5) {
        return new FrontLightRestingMovingGimbalState(
            this->getEventBus(), this->getLightsStripDriver(),
            movementEvent->getHorizontalAngle());
      }
    } else {
      return new FrontLightRestingState(this->getEventBus(),
                                        this->getLightsStripDriver());
    }
  } else if (strcmp(event->getEventKey(), LightEvent::LIGHT_FRONT_OFF) == 0) {
    return new FrontLightOffState(this->getEventBus(),
                                  this->getLightsStripDriver());
  }
  return this;
}

// Operations ###########################

/*
 * Shows degrade light proportional to the angle of the gimbal
 */
void FrontLightRestingMovingGimbalState::showLights(int horizontalAngle) {
  if (horizontalAngle <= LEFT_LIGHT_ANGLE) {
    float percAngle = (horizontalAngle / LEFT_LIGHT_ANGLE);
    int steps = (NUM_ALWAYS_PIXELS_ON +
                 ((NUM_PIXELS_ON - NUM_ALWAYS_PIXELS_ON) * percAngle));
    float brightness = MAX_BRIGHTNESS;
    float brightness_dec = brightness / steps;
    for (int i = 7; i >= 0; i--) {
      if (brightness > 0) {
        this->getLightsStripDriver()->showPixel(i, LightsStripDriver::BLUE(),
                                                brightness);
      } else {
        this->getLightsStripDriver()->showPixel(i, 0, 0, 0, 0.0);
      }
      brightness -= brightness_dec;
    }
    this->getLightsStripDriver()->show();
  } else if (horizontalAngle >= RIGHT_LIGHT_ANGLE) {
    float percAngle =
        1.0 -
        (((horizontalAngle - RIGHT_LIGHT_ANGLE) / (180 - RIGHT_LIGHT_ANGLE)));
    int steps = (NUM_ALWAYS_PIXELS_ON +
                 ((NUM_PIXELS_ON - NUM_ALWAYS_PIXELS_ON) * percAngle));
    float brightness = MAX_BRIGHTNESS;
    float brightness_dec = brightness / steps;
    for (int i = 0; i <= 7; i++) {
      if (brightness > 0) {
        this->getLightsStripDriver()->showPixel(i, LightsStripDriver::BLUE(),
                                                brightness);
      } else {
        this->getLightsStripDriver()->showPixel(i, 0, 0, 0, 0.0);
      }
      brightness -= brightness_dec;
    }
    this->getLightsStripDriver()->show();
  }
}

#endif