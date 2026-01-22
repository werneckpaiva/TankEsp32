#ifndef GimbalEvent_h
#define GimbalEvent_h

#include <Arduino.h>
#include <EventDrivenStates.h>

class MoveGimbalEvent : public Event {
private:
  int horizontalAngle;
  int verticalAngle;
  char *buffer = nullptr;

public:
  static constexpr const char *MOVE_GIMBAL = "gimbal.move";

  const char *getEventKey() { return MoveGimbalEvent::MOVE_GIMBAL; }

  MoveGimbalEvent(int horizontalAngle, int verticalAngle) {
    this->horizontalAngle = horizontalAngle;
    this->verticalAngle = verticalAngle;
  }

  int getHorizontalAngle() { return this->horizontalAngle; }

  int getVerticalAngle() { return this->verticalAngle; }

  virtual ~MoveGimbalEvent() {
    if (buffer != nullptr) {
      delete[] buffer;
    }
  }

  const char *toString() override {
    if (buffer == nullptr) {
      buffer = new char[64];
    }
    snprintf(buffer, 64, "%s: H=%d V=%d", getEventKey(), horizontalAngle,
             verticalAngle);
    return buffer;
  }
  Event *clone() const override {
    MoveGimbalEvent *newEvent = new MoveGimbalEvent(*this);
    newEvent->buffer = nullptr; // Ensure the clone has its own buffer management
    return newEvent;
  }
};

#endif