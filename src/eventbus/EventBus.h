#ifndef EventBus_h
#define EventBus_h

#include <Arduino.h>
#include "freertos/task.h"
#include "freertos/queue.h"


class Event{
  public:
    virtual const char* getEventId();
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
    EventListener();
    virtual void receiveEvent(Event *event){};
};

EventListener::EventListener(){
    this->eventQueue = xQueueCreate(5, sizeof(Event*));
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
    Event *event;
    for(;;){
        if(xQueueReceive(
            self->eventQueue,
            &event,
            portMAX_DELAY) == pdPASS){

            self->receiveEvent(event);
        }
    }
}

class ListenerNode{
  private:
    char* eventKey;
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
        QueueHandle_t queue;
        ListenerNode *rootListenerList;
        static void dispatcherTask(void *params);

    public:
        EventBus(byte queueSize);
        void addEventListener(EventListener *listener);
        void removeEventListener(EventListener *listener);
        void dispatchEvent(Event *event);
};

EventBus::EventBus(byte queueSize){
    this->queue = xQueueCreate(queueSize, sizeof(Event*));
    xTaskCreatePinnedToCore(EventBus::dispatcherTask,
                "Dispatcher",
                2 * 1024,
                (void *) this,
                1,
                NULL,
                0);
};

void EventBus::addEventListener(EventListener *listener){
    ListenerNode *current = this->rootListenerList;
    EventBus::rootListenerList = new ListenerNode(listener, current);
}

void EventBus::removeEventListener(EventListener *listener){
    ListenerNode *current = this->rootListenerList;
    while(current != NULL){
        if (current->getListener() == listener){

        }
    }
}

void EventBus::dispatchEvent(Event *event){
    if (xQueueSend(EventBus::queue, (void *) &event, 50 / portTICK_PERIOD_MS) != pdPASS){
        Serial.println("Queue full!");
    }
}

void EventBus::dispatcherTask(void *params){
    EventBus *self = (EventBus *) params;
    for(;;){
        Event *event;
        BaseType_t hasMessage = xQueueReceive(
            self->queue,
            &event,
            (300000 / portTICK_PERIOD_MS));
        if(hasMessage == pdPASS){
            Serial.printf("Dispatcher: message received type: %s\n", event->getEventId());
            ListenerNode *currentListenerNode = self->rootListenerList;
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