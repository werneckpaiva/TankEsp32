#ifndef EventBus_h
#define EventBus_h

#include <Arduino.h>
#include "freertos/task.h"
#include "freertos/queue.h"


class Event{
  public:
    virtual const char* getEventKey();
    virtual Event* clone();
    virtual ~Event(){}
};

/**
 * @brief Task that receives the events of a given type.
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
 * @brief Construct a new Event Listener
 * 
 * @param memorySize the memory used by the FreeRTOS Task that will receive messages (kBytes)
 * @param eventQueueSize Amount of messages that can be stored in the event queue
 */
EventListener::EventListener(unsigned int memorySize, byte eventQueueSize){
    this->eventQueue = xQueueCreate(eventQueueSize, sizeof(Event*));
    xTaskCreate(EventListener::listenerTask,
                "EventListener",
                memorySize * 1024,
                (void *) this,
                10,
                NULL);
}


void EventListener::listenerTask(void *params){
    EventListener *self = (EventListener *) params;
    Event *event;
    for(;;){
        if(xQueueReceive(self->eventQueue, &event, portMAX_DELAY) == pdPASS){
            self->receiveEvent(event);
        }
    }
}

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
 * @brief Contains the message bus where events are sent to
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

EventBus::EventBus(byte queueSize){
    this->queue = xQueueCreate(queueSize, 4 * sizeof(Event*));
    xTaskCreate(EventBus::dispatcherTask,
                "Dispatcher",
                5 * 1024,
                (void *) this,
                1,
                NULL);
};

void EventBus::addEventListener(const char* eventKeyPrefix, EventListener *listener){
    ListenerNode *current = this->rootListenerList;
    EventBus::rootListenerList = new ListenerNode(eventKeyPrefix, listener, current);
}

void EventBus::removeEventListener(EventListener *listener){
    ListenerNode *current = this->rootListenerList;
    while(current != NULL){
        if (current->getListener() == listener){

        }
    }
}

void EventBus::dispatchEvent(Event *event){
    if (xQueueSend(this->queue, (void *) &event, portMAX_DELAY) != pdPASS){
        Serial.println("EVENT_BUS: Queue full!");
    }
}

void EventBus::dispatcherTask(void *params){
    EventBus *self = (EventBus *) params;
    for(;;){
        Event *event;
        BaseType_t hasMessage = xQueueReceive(
            self->queue,
            &event,
            portMAX_DELAY);
        if(hasMessage == pdPASS){
            ListenerNode *currentListenerNode = self->rootListenerList; 
            while(currentListenerNode != NULL){
                // Does the event key contain the  listener keyprefix? 
                if (strncmp(
                        event->getEventKey(),
                        currentListenerNode->getEventKeyPrefix(), 
                        strlen(currentListenerNode->getEventKeyPrefix())) == 0){
                        if (xQueueSend(
                                currentListenerNode->getListener()->eventQueue,
                                (void *) &event,
                                0) != pdPASS){
                            Serial.println("EVENT_BUS: Listener Queue full!");
                        }
                }
                
                currentListenerNode = currentListenerNode->getNext();
            }
            delete(event);
        }
    }
}

#endif