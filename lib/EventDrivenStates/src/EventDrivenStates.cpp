
#include "EventDrivenStates.h"

#include <Arduino.h>
#include "freertos/task.h"
#include "freertos/queue.h"

/**
 * @brief Construct a new Event Listener
 *
 * @param memorySize the memory used by the FreeRTOS Task that will receive
 * messages (kBytes)
 * @param eventQueueSize Amount of messages that can be stored in the event
 * queue
 */
EventListener::EventListener(unsigned int memorySize, byte eventQueueSize) {
  this->eventQueue = xQueueCreate(eventQueueSize, sizeof(Event *));
  xTaskCreate(EventListener::listenerTask, "EventListener", memorySize * 1024,
              (void *)this, 10, NULL);
}

void EventListener::listenerTask(void *params) {
  EventListener *self = (EventListener *)params;
  Event *event;
  for (;;) {
    if (xQueueReceive(self->eventQueue, &event, portMAX_DELAY) == pdPASS) {
      self->receiveEvent(event);
      delete event;
    }

  }
}

EventBus::EventBus(byte queueSize) {
  this->queue = xQueueCreate(queueSize, 4 * sizeof(Event *));
  xTaskCreate(EventBus::dispatcherTask, "Dispatcher", 5 * 1024, (void *)this, 1, NULL);
};

void EventBus::addEventListener(const char *eventKeyPrefix,
                                EventListener *listener) {
  ListenerNode *current = this->rootListenerList;
  EventBus::rootListenerList =
      new ListenerNode(eventKeyPrefix, listener, current);
}

void EventBus::removeEventListener(EventListener *listener) {
  ListenerNode *current = this->rootListenerList;
  while (current != NULL) {
    if (current->getListener() == listener) {
    }
  }
}

void EventBus::dispatchEvent(Event *event) {
  if (xQueueSend(this->queue, (void *)&event, portMAX_DELAY) != pdPASS) {
    Serial.println("EVENT_BUS: Queue full!");
  }
}

void EventBus::dispatcherTask(void *params) {
  EventBus *self = (EventBus *)params;
  for (;;) {
    Event *event;
    BaseType_t hasMessage = xQueueReceive(self->queue, &event, portMAX_DELAY);
    if (hasMessage == pdPASS) {
      ListenerNode *currentListenerNode = self->rootListenerList;
      while (currentListenerNode != NULL) {
        // Does the event key contain the  listener keyprefix?
        if (strncmp(event->getEventKey(),
                    currentListenerNode->getEventKeyPrefix(),
                    strlen(currentListenerNode->getEventKeyPrefix())) == 0) {
          Event *clonedEvent = event->clone();
          if (xQueueSend(currentListenerNode->getListener()->eventQueue,
                         (void *)&clonedEvent, 0) != pdPASS) {
            Serial.println("EVENT_BUS: Listener Queue full!");
            delete clonedEvent; // Prevent leak if queue full
          }
        }

        currentListenerNode = currentListenerNode->getNext();
      }
      delete (event);
    }
  }
}

StatefulController::StatefulController(State *initialState) {
  this->currentState = initialState;
}

void StatefulController::receiveEvent(Event *event) {
  Serial.printf("StatefulController: event received: %s\n", event->toString());
  State *oldState = this->currentState;
  this->currentState = this->currentState->transition(event);
  if (oldState != this->currentState) {
    delete (oldState);
  }
}