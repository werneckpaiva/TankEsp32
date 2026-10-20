#ifndef FrontLightsState_h
#define FrontLightsState_h

#include <Arduino.h>
#include <EventDrivenStates.h>
#include "drivers/LightsStripDriver.h"
#include "events/LightEvent.h"
#include "events/MovementEvent.h"
#include "events/GimbalEvent.h"


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
 * Lights off: the strip stays cleared until light.front.on
 */
class FrontLightOffState : public LightState {
public:
  FrontLightOffState(EventBus *eventBus, LightsStripDriver *lightsStripDriver) : LightState(eventBus, lightsStripDriver) {
    lightsStripDriver->clear();
  }
  State *transition(Event *event);
};

/*
 * Lights on while stopped and the gimbal is centred: solid blue
 */
class FrontLightRestingState : public LightState {
public:
  FrontLightRestingState(EventBus *eventBus, LightsStripDriver *lightsStripDriver) : LightState(eventBus, lightsStripDriver) {
    lightsStripDriver->fullPaint(LightsStripDriver::BLUE(), 1);
  }
  State *transition(Event *event);
};

/*
 * Driving: the whole strip in the direction's colour, brighter with speed
 */
class FrontLightMovingState : public LightState {
  static constexpr const float MAX_BRIGHTNESS = 0.7;
  static constexpr const double MAX_SPEED = 255.0;

public:
  FrontLightMovingState(EventBus *eventBus, LightsStripDriver *lightsStripDriver, int speed, const byte *color) : LightState(eventBus, lightsStripDriver) {
    float brightness = abs((speed / MAX_SPEED) * MAX_BRIGHTNESS);
    lightsStripDriver->fullPaint(color, brightness);
  }
  State *transition(Event *event);
};

class FrontLightMovingForwardState : public FrontLightMovingState {
public:
  FrontLightMovingForwardState(EventBus *eventBus, LightsStripDriver *lightsStripDriver, int speed) : FrontLightMovingState(eventBus, lightsStripDriver, speed, LightsStripDriver::GREEN()) {}
};

class FrontLightMovingBackwardState : public FrontLightMovingState {
public:
  FrontLightMovingBackwardState(EventBus *eventBus, LightsStripDriver *lightsStripDriver, int speed) : FrontLightMovingState(eventBus, lightsStripDriver, speed, LightsStripDriver::RED()) {}
};

/*
 * Stopped with the gimbal panned outside LEFT_LIGHT_ANGLE..RIGHT_LIGHT_ANGLE:
 * a blue gradient from the end of the strip on the pan side
 */
class FrontLightRestingMovingGimbalState : public LightState {
private:
  int horizontalAngle;

public:
  // The gimbal counts as centred between these pan angles
  static constexpr const float LEFT_LIGHT_ANGLE = 80.0;
  static constexpr const float RIGHT_LIGHT_ANGLE = 100.0;
  static constexpr const float MAX_ANGLE = 180;
  // Smaller pan changes than this keep the current gradient
  static const int MIN_ANGLE_CHANGE = 5;
  static constexpr const float NUM_PIXELS_ON = 8;
  static constexpr const float NUM_ALWAYS_PIXELS_ON = 2;
  static const int LAST_PIXEL = 7;
  static constexpr const float MAX_BRIGHTNESS = .5;
  FrontLightRestingMovingGimbalState(EventBus *eventBus, LightsStripDriver *lightsStripDriver, int horizontalAngle) : LightState(eventBus, lightsStripDriver) {
    this->horizontalAngle = horizontalAngle;
    this->showLights(horizontalAngle);
  }
  void showLights(int horizontalAngle);
  void showGradient(float spread, bool fromLastPixel);
  State *transition(Event *event);
};

// Transitions  #################################

State *FrontLightOffState::transition(Event *event) {
  if (event->is(LightEvent::LIGHT_FRONT_ON)) {
    State* newState = new FrontLightRestingState(this->getEventBus(), this->getLightsStripDriver());
    DEBUG_PRINTF("New state address: %p\n", newState);
    return newState;
  }
  return this;
}

State *FrontLightRestingState::transition(Event *event) {
  if (event->is(MovementEvent::FORWARD)) {
    MovementWithSpeedEvent *movementEvent = (MovementWithSpeedEvent *)event;
    return new FrontLightMovingForwardState(this->getEventBus(), this->getLightsStripDriver(), movementEvent->getVerticalSpeed());
  } else if (event->is(MovementEvent::BACKWARD)) {
    MovementWithSpeedEvent *movementEvent = (MovementWithSpeedEvent *)event;
    return new FrontLightMovingBackwardState(this->getEventBus(), this->getLightsStripDriver(), movementEvent->getVerticalSpeed());
  } else if (event->is(MoveGimbalEvent::MOVE_GIMBAL)) {
    MoveGimbalEvent *gimbalEvent = (MoveGimbalEvent *)event;
    return new FrontLightRestingMovingGimbalState(this->getEventBus(), this->getLightsStripDriver(), gimbalEvent->getHorizontalAngle());
  } else if (event->is(LightEvent::LIGHT_FRONT_OFF)) {
    return new FrontLightOffState(this->getEventBus(), this->getLightsStripDriver());
  }
  return this;
}

State *FrontLightMovingState::transition(Event *event) {
  if (event->is(MovementEvent::STOP)) {
    return new FrontLightRestingState(this->getEventBus(), this->getLightsStripDriver());
  } else if (event->is(MovementEvent::FORWARD)) {
    MovementWithSpeedEvent *movementEvent = (MovementWithSpeedEvent *)event;
    return new FrontLightMovingForwardState(this->getEventBus(), this->getLightsStripDriver(), movementEvent->getVerticalSpeed());
  } else if (event->is(MovementEvent::BACKWARD)) {
    MovementWithSpeedEvent *movementEvent = (MovementWithSpeedEvent *)event;
    return new FrontLightMovingBackwardState(this->getEventBus(), this->getLightsStripDriver(), movementEvent->getVerticalSpeed());
  } else if (event->is(LightEvent::LIGHT_FRONT_OFF)) {
    return new FrontLightOffState(this->getEventBus(), this->getLightsStripDriver());
  }
  return this;
}

State *FrontLightRestingMovingGimbalState::transition(Event *event) {
  if (event->is(MoveGimbalEvent::MOVE_GIMBAL)) {
    int angle = ((MoveGimbalEvent *)event)->getHorizontalAngle();
    bool centred = angle >= LEFT_LIGHT_ANGLE && angle <= RIGHT_LIGHT_ANGLE;
    if (centred) {
      return new FrontLightRestingState(this->getEventBus(), this->getLightsStripDriver());
    }
    if (abs(this->horizontalAngle - angle) > MIN_ANGLE_CHANGE) {
      return new FrontLightRestingMovingGimbalState(this->getEventBus(), this->getLightsStripDriver(), angle);
    }
  } else if (event->is(LightEvent::LIGHT_FRONT_OFF)) {
    return new FrontLightOffState(this->getEventBus(), this->getLightsStripDriver());
  }
  return this;
}

// Operations ###########################

/*
 * Shows a gradient on the side the gimbal is panned to. The further the pan,
 * the fewer pixels it spreads over (spread 0 at the extremes, 1 near centre).
 */
void FrontLightRestingMovingGimbalState::showLights(int horizontalAngle) {
  if (horizontalAngle <= LEFT_LIGHT_ANGLE) {
    float spread = (horizontalAngle / LEFT_LIGHT_ANGLE);
    this->showGradient(spread, true);
  } else if (horizontalAngle >= RIGHT_LIGHT_ANGLE) {
    float spread = 1.0 - (((horizontalAngle - RIGHT_LIGHT_ANGLE) / (MAX_ANGLE - RIGHT_LIGHT_ANGLE)));
    this->showGradient(spread, false);
  }
}

/*
 * Lights the strip in blue starting at full brightness on one end and fading
 * out over NUM_ALWAYS_PIXELS_ON (spread 0) to NUM_PIXELS_ON (spread 1) pixels.
 */
void FrontLightRestingMovingGimbalState::showGradient(float spread, bool fromLastPixel) {
  int steps = (NUM_ALWAYS_PIXELS_ON + ((NUM_PIXELS_ON - NUM_ALWAYS_PIXELS_ON) * spread));
  float brightness = MAX_BRIGHTNESS;
  float brightnessStep = brightness / steps;
  for (int n = 0; n <= LAST_PIXEL; n++) {
    int pixel = fromLastPixel ? LAST_PIXEL - n : n;
    if (brightness > 0) {
      this->getLightsStripDriver()->showPixel(pixel, LightsStripDriver::BLUE(), brightness);
    } else {
      this->getLightsStripDriver()->showPixel(pixel, 0, 0, 0, 0.0);
    }
    brightness -= brightnessStep;
  }
  this->getLightsStripDriver()->show();
}

#endif