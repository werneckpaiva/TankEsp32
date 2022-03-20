#ifndef EventBus_h
#define EventBus_h

#include <Arduino.h>
#include "freertos/task.h"
#include "freertos/queue.h"


class EventBase{
  public:
    virtual int eventType();
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
    EventListener();
    virtual void receiveEvent(EventBase *event){};
};

EventListener::EventListener(){
    this->eventQueue = xQueueCreate(4, sizeof(EventBase*));
    xTaskCreatePinnedToCore(EventListener::listenerTask,
                "EventListener",
                2 * 1024,
                (void *) this,
                1,
                NULL,
                1);
}

void EventListener::listenerTask(void *params){
    EventListener *self = (EventListener *) params;
    EventBase *event;
    for(;;){
        if(xQueueReceive(
            self->eventQueue,
            &event,
            (300000 / portTICK_PERIOD_MS)) == pdPASS){

            self->receiveEvent(event);
        }
    }
}

class ListenerNode{
  private:
    EventListener *listener;
    ListenerNode *next;
  public:

    ListenerNode(EventListener *listener, ListenerNode *current = NULL) {
      this->listener = listener;
      this->next = current;
    }

    EventListener* getListener(){
      return this->listener;
    }

    ListenerNode* getNext(){
      return this->next;
    }
};

/**
 * @brief Contains the message bus where all events are sent to
 * 
 */
class EventBus{
    private:
        static QueueHandle_t queue;
        static ListenerNode *rootListenerList;
        static void dispatcherTask(void *params);

    public:
        static void init(byte queueSize);
        static void addEventListener(EventListener *listener);
        static void dispatchEvent(EventBase *event);
};

QueueHandle_t EventBus::queue;
ListenerNode *EventBus::rootListenerList;

void EventBus::init(byte queueSize){
    EventBus::queue = xQueueCreate(queueSize, sizeof(EventBase*));
    xTaskCreatePinnedToCore(EventBus::dispatcherTask,
                "Dispatcher",
                2 * 1024,
                NULL,
                1,
                NULL,
                0);
};

void EventBus::addEventListener(EventListener *listener){
    ListenerNode *current = EventBus::rootListenerList;
    EventBus::rootListenerList = new ListenerNode(listener, current);
}

void EventBus::dispatchEvent(EventBase *event){
    if (xQueueSend(EventBus::queue, (void *) &event, 50 / portTICK_PERIOD_MS) != pdPASS){
        Serial.println("Queue full!");
    }
}

void EventBus::dispatcherTask(void *params){
    for(;;){
        EventBase *event;
        BaseType_t hasMessage = xQueueReceive(
            EventBus::queue,
            &event,
            (300000 / portTICK_PERIOD_MS));
        if(hasMessage == pdPASS){
            Serial.printf("Dispatcher: message received type: %d\n", event->eventType());
            ListenerNode *currentListenerNode = EventBus::rootListenerList;
            while(currentListenerNode != NULL){
                if (xQueueSend(
                        currentListenerNode->getListener()->eventQueue,
                        (void *) &event,
                        10 / portTICK_PERIOD_MS) != pdPASS){
                    Serial.println("Listener Queue full!");
                }
                
                currentListenerNode = currentListenerNode->getNext();
            }
            Serial.println("deleting");
            delete(event);
        }
    }
}

#endif