#ifndef EventBus_h
#define EventBus_h

#include <Arduino.h>
#include "freertos/task.h"
#include "freertos/queue.h"


class EventBase{
  public:
    virtual uint16_t getEventTypeId();
};

/**
 * @brief Task that receives the events of a given type.
 * 
 */
class EventListener{
  public: virtual void receiveEvent(EventBase *event);
};

/**
 * @brief Routes the mesages in the messagebus to the right listeners
 * 
 */
class EventDispatcher{
    private:
        QueueHandle_t *queue;
        static void dispatcherTask(void *params);
    public:
        EventDispatcher(QueueHandle_t *queue);
};

/**
 * @brief Contains the message bus where all events are sent to
 * 
 */
class EventBus{
    private:
        static EventDispatcher *dispatcher;
        static QueueHandle_t queue;

    public:
        static void init(byte queueSize);
        static void addEventListener(uint16_t eventTypeId, EventListener *eventListener);
        static void dispatchEvent(EventBase *event);
};

QueueHandle_t EventBus::queue;
EventDispatcher *EventBus::dispatcher;

void EventBus::init(byte queueSize){
    EventBus::queue = xQueueCreate(queueSize, sizeof(EventBase*));
    EventBus::dispatcher = new EventDispatcher(&EventBus::queue);
};

void EventBus::addEventListener(uint16_t eventTypeId, EventListener *eventListener){

}

void EventBus::dispatchEvent(EventBase *event){
    if (xQueueSend(EventBus::queue, (void *) &event, 50 / portTICK_PERIOD_MS) != pdPASS){
        Serial.println("Queue full!");
    }
}


EventDispatcher::EventDispatcher(QueueHandle_t *queue){
    this->queue = queue;
    xTaskCreate(EventDispatcher::dispatcherTask,
                "dispatcher",
                2 * 1024,
                (void *) this,
                1,
                NULL);
}

void EventDispatcher::dispatcherTask(void *params){
    EventDispatcher *self = (EventDispatcher*) params;
    for(;;){
        EventBase *event;
        BaseType_t hasMessage = xQueueReceive(
            *self->queue,
            &event,
            (1000 * 60 * 5 / portTICK_PERIOD_MS));
        if(hasMessage == pdPASS){
            Serial.printf("Message received type: %d\n", event->getEventTypeId());
        }
    }
}

#endif