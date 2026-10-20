#ifndef EventDrivenStates_h
#define EventDrivenStates_h

#include <Arduino.h>
#include "freertos/task.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"

/**
 * Debug output, compiled in only when DEBUG_MODE is defined (build_flags in
 * platformio.ini). When disabled the call and its arguments are removed
 * entirely, so arguments are not evaluated.
 */
#ifdef DEBUG_MODE
#define DEBUG_PRINTF(...) Serial.printf(__VA_ARGS__)
#define DEBUG_PRINTLN(msg) Serial.println(msg)
#else
#define DEBUG_PRINTF(...) do {} while (0)
#define DEBUG_PRINTLN(msg) do {} while (0)
#endif



/**
 * @brief The representation of an event.
 *
 * All events must inherit from Events.
 * They must implement getEventKey as an unique key.
 *
 */
class Event {
public:
  virtual const char *getEventKey() = 0;
  virtual ~Event() {}
  virtual Event* clone() const = 0;
  virtual const char *toString() { return this->getEventKey(); }
};

/**
 * @brief Receives the events of a given type.
 *
 * It works as an independent task receiving messages from the bus
 *
 */
class EventListener {
private:
  static void listenerTask(void *params);
  TaskHandle_t taskHandle = NULL;

public:
  QueueHandle_t eventQueue;
  EventListener(unsigned int memorySize = 3, byte eventQueueSize = 3);
  virtual void receiveEvent(Event *event) {};
  // Minimum free stack (bytes) the listener task has had since it started
  unsigned int getStackHighWaterMark();
};

/**
 * @brief An entry on the list of EventListeners of a given event type.
 *
 */
class ListenerNode {
private:
  const char *eventKeyPrefix;
  EventListener *listener;
  ListenerNode *next = NULL;

public:
  ListenerNode(const char *eventKeyPrefix, EventListener *listener,
               ListenerNode *current = NULL) {
    this->eventKeyPrefix = eventKeyPrefix;
    this->listener = listener;
    this->next = current;
  }

  EventListener *getListener() { return this->listener; }

  ListenerNode *getNext() { return this->next; }

  void setNext(ListenerNode *next) { this->next = next; }

  const char *getEventKeyPrefix() { return this->eventKeyPrefix; };
};

/**
 * @brief The message bus where events are sent to. It uses the FreeRTOS Queue
 * system to enqueue the messages and dispatch to the event listeners.
 *
 */
class EventBus {
private:
  QueueHandle_t queue;
  ListenerNode *rootListenerList = NULL;
  // Guards rootListenerList: the dispatcher task walks it while other tasks
  // may add or remove listeners.
  SemaphoreHandle_t listenersMutex;
  static void dispatcherTask(void *params);

public:
  EventBus(byte queueSize);
  void addEventListener(const char *eventKeyPrefix, EventListener *listener);
  // Unregisters every prefix of the listener. The listener itself is not deleted.
  void removeEventListener(EventListener *listener);
  void dispatchEvent(Event *event);
};

/**
 * @brief A representation of a state. It should be inherited and implement the
 *
 */
class State {
private:
  EventBus *eventBus;

public:
  State(EventBus *eventBus) { this->eventBus = eventBus; }

  EventBus *getEventBus() { return this->eventBus; }

  virtual State *transition(Event *event) = 0;
  virtual ~State() {}
};

class StatefulController : public EventListener {
private:
  State *currentState = NULL;

public:
  StatefulController(State *initialState);
  void receiveEvent(Event *event);
};

#endif