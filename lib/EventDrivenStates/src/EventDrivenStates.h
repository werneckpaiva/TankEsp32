#ifndef EventDrivenStates_h
#define EventDrivenStates_h

#include <Arduino.h>
#include "freertos/task.h"
#include "freertos/queue.h"

/**
 * @brief The representation of an event. 
 * 
 * All events must inherit from Events.
 * They must implement getEventKey as an unique key.
 * 
 */
class Event{
  public:
    virtual const char* getEventKey();
    virtual ~Event(){}
    const char* toString(){
        return this->getEventKey();
    }
};

/**
 * @brief Receives the events of a given type.
 * 
 * It works as an independent task receiving messages from the bus
 * 
 */
class EventListener{
  private:
    static void listenerTask(void *params);
  public:
    QueueHandle_t eventQueue;
    EventListener(unsigned int memorySize=2, byte eventQueueSize=3);
    virtual void receiveEvent(Event *event){};
};

/**
 * @brief An entry on the list of EventListeners of a given event type.
 * 
 */
class ListenerNode{
  private:
    const char* eventKeyPrefix;
    EventListener *listener;
    ListenerNode *next = NULL;
  public:

    ListenerNode(const char* eventKeyPrefix, EventListener *listener, ListenerNode *current = NULL) {
        this->eventKeyPrefix = eventKeyPrefix;
        this->listener = listener;
        this->next = current;
    }

    EventListener* getListener(){
        return this->listener;
    }

    ListenerNode* getNext(){
        return this->next;
    }

    const char* getEventKeyPrefix(){
        return this->eventKeyPrefix;
    };
};

/**
 * @brief The message bus where events are sent to. It uses the FreeRTOS Queue system to enqueue the messages and dispatch to the event listeners.
 * 
 */
class EventBus{
    private:
        QueueHandle_t queue;
        ListenerNode *rootListenerList = NULL;
        static void dispatcherTask(void *params);

    public:
        EventBus(byte queueSize);
        void addEventListener(const char* eventKeyPrefix, EventListener *listener);
        void removeEventListener(EventListener *listener);
        void dispatchEvent(Event *event);
};

/**
 * @brief A representation of a state. It should be inherited and implement the 
 * 
 */
class State{
    private:
      EventBus *eventBus;

    public:
      State(EventBus *eventBus){
        this->eventBus = eventBus;
      }

      EventBus* getEventBus(){
        return this->eventBus;
      }

      virtual State* transition(Event *event);
      virtual ~State(){}
};

class StatefulController : public EventListener {
  private:
    State *currentState = NULL;
  public:
    StatefulController(State *initialState);
    void receiveEvent(Event *event);
};

#endif