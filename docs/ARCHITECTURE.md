# Architecture

TankEsp32 is event-driven. One component reads the RC receiver and publishes events to an `EventBus`. Each subsystem (movement, gimbal, front lights) has its own `StatefulController`. Each controller holds a state machine, receives events whose key matches its prefix, and drives its hardware through a driver.

The framework classes are defined in [`lib/EventDrivenStates`](../lib/EventDrivenStates/src/EventDrivenStates.h). The objects are wired together in [`src/main.cpp`](../src/main.cpp).

## Components and event flow

All controllers are active in `main.cpp`.

```mermaid
flowchart LR
    subgraph HW_IN[Input hardware]
        RX[FlySky iBus receiver<br/>Serial2]
    end

    subgraph SOURCE[Event source]
        RCD[RCDriver]
        RCS["rcMonitor: RCMonitoringState<br/>readRC task, every 50 ms"]
        RX --> RCD --> RCS
    end

    subgraph BUS[EventBus]
        Q[(Bus queue<br/>size 10)]
        DISP["Dispatcher task<br/>prefix match + clone()"]
        Q --> DISP
    end

    RCS -- "dispatchEvent(new Event)" --> Q

    subgraph CONSUMERS[Listeners: one FreeRTOS task + queue each]
        FLC["frontLightsController<br/>prefix: '' (all events)"]
        MC["movementController<br/>prefix: 'movement.'"]
        GC["gimbalController<br/>prefix: 'gimbal.'"]
    end

    DISP -- clone --> FLC
    DISP -- clone --> MC
    DISP -- clone --> GC

    subgraph DRIVERS[Drivers]
        LSD[LightsStripDriver]
        WMD[WheelsMotorDriver]
        GD[GimbalDriver]
    end

    FLC --> LSD --> LED[NeoPixel strip<br/>GPIO 27]
    MC --> WMD --> MOT[DC motors<br/>GPIO 18/19/22/23]
    GC --> GD --> SRV[Pan/tilt servos<br/>GPIO 25/26]

```

## Event lifecycle and ownership

Events are heap-allocated and short-lived. The bus deletes the original after fan-out. Each listener receives its own clone and deletes it after `receiveEvent()` returns. If `transition()` returns a different state, the controller deletes the old one.

```mermaid
sequenceDiagram
    participant RC as RCMonitoringState (readRC task)
    participant Bus as EventBus queue
    participant D as Dispatcher task
    participant LQ as Listener queue
    participant L as Listener task
    participant SC as StatefulController
    participant S as Current State

    RC->>Bus: dispatchEvent(new MovementForwardEvent)
    Bus->>D: xQueueReceive
    loop for each registered listener
        D->>D: strncmp(eventKey, prefix)
        alt prefix matches
            D->>LQ: xQueueSend(event->clone(), timeout 0)
            Note over D,LQ: Queue full: log and delete the clone (event dropped)
        end
    end
    D->>D: delete original event
    LQ->>L: xQueueReceive
    L->>SC: receiveEvent(clone)
    SC->>S: transition(clone)
    alt returns a new State
        S-->>SC: new NextState(...)<br/>(constructor drives the hardware)
        SC->>SC: delete old state
    else returns this
        S-->>SC: this
    end
    L->>L: delete clone
```

## Framework classes

```mermaid
classDiagram
    class Event {
        <<abstract>>
        +getEventKey() const char*
        +clone() Event*
        +toString() const char*
    }
    class EventListener {
        +QueueHandle_t eventQueue
        +EventListener(memorySizeKB = 3, queueSize = 3)
        +getStackHighWaterMark() unsigned int
        +receiveEvent(Event*)
        -listenerTask(void*)$
    }
    class EventBus {
        -QueueHandle_t queue
        -ListenerNode* rootListenerList
        +EventBus(queueSize)
        +addEventListener(prefix, EventListener*)
        +removeEventListener(EventListener*)
        -SemaphoreHandle_t listenersMutex
        +dispatchEvent(Event*)
        -dispatcherTask(void*)$
    }
    class ListenerNode {
        -const char* eventKeyPrefix
        -EventListener* listener
        -ListenerNode* next
    }
    class State {
        <<abstract>>
        -EventBus* eventBus
        +transition(Event*) State*
    }
    class StatefulController {
        -State* currentState
        +receiveEvent(Event*)
    }

    EventListener <|-- StatefulController
    EventBus "1" o-- "*" ListenerNode
    ListenerNode --> EventListener
    StatefulController --> State : currentState
    State --> EventBus : dispatches to

    Event <|-- MovementEvent
    Event <|-- MoveGimbalEvent
    Event <|-- LightEvent
    MovementEvent <|-- MovementStopEvent
    MovementEvent <|-- MovementWithSpeedEvent
    MovementWithSpeedEvent <|-- MovementForwardEvent
    MovementWithSpeedEvent <|-- MovementBackwardEvent
    MovementWithSpeedEvent <|-- MovementSpinRightEvent
    MovementWithSpeedEvent <|-- MovementSpinLeftEvent
    LightEvent <|-- TurnFrontLightOnEvent
    LightEvent <|-- TurnFrontLightOffEvent

    State <|-- RCMonitoringState
    State <|-- MovementState
    State <|-- ManualControlState
    State <|-- LightState
```

## Event keys

| Key | Class | Payload | Emitted when |
|---|---|---|---|
| `movement.forward` | `MovementForwardEvent` | horizontal, vertical speed | throttle > 10 |
| `movement.backward` | `MovementBackwardEvent` | horizontal, vertical speed | throttle < -10 |
| `movement.spin.right` | `MovementSpinRightEvent` | speed | throttle in ±10 and turn > 10 |
| `movement.spin.left` | `MovementSpinLeftEvent` | speed | throttle in ±10 and turn < -10 |
| `movement.stop` | `MovementStopEvent` | none | both sticks centred |
| `gimbal.move` | `MoveGimbalEvent` | horizontal, vertical angle | tilt or pan changed |
| `light.front.on` / `light.front.off` | `TurnFrontLight{On,Off}Event` | none | lights switch toggled |

`RCMonitoringState` emits events only when channel values change. RC input is continuous, so an occasional dropped event is accepted: the next change supersedes it.

## State machines

### Movement ([`MovementState.h`](../src/states/MovementState.h))

The constructor of each state drives the motors. Changing direction (including spin → forward/backward) always passes through `Stopped`; the next forward/backward event starts the new move. A self-transition builds a new state with the new speed.

```mermaid
stateDiagram-v2
    direction LR
    [*] --> Stopped
    Stopped --> MoveForward : movement.forward
    Stopped --> MoveBackward : movement.backward
    Stopped --> SpinningRight : movement.spin.right
    Stopped --> SpinningLeft : movement.spin.left

    MoveForward --> MoveForward : movement.forward (new speed)
    MoveForward --> Stopped : movement.stop / movement.backward

    MoveBackward --> MoveBackward : movement.backward (new speed)
    MoveBackward --> Stopped : movement.stop / movement.forward

    SpinningRight --> SpinningRight : movement.spin.right (new speed)
    SpinningRight --> Stopped : stop / spin.left / forward / backward

    SpinningLeft --> SpinningLeft : movement.spin.left (speed change > 5)
    SpinningLeft --> Stopped : stop / spin.right / forward / backward
```

### Front lights ([`FrontLighstState.h`](../src/states/FrontLighstState.h))

This controller listens to every event (prefix `""`) because it reacts to movement and gimbal events as well as light events. `MovingForward` and `MovingBackward` share the transition logic in `FrontLightMovingState`.

```mermaid
stateDiagram-v2
    state "Off — strip cleared" as Off
    state "Resting — solid blue" as Resting
    state "MovingForward — green, brightness ∝ speed" as MovingForward
    state "MovingBackward — red, brightness ∝ speed" as MovingBackward
    state "RestingMovingGimbal — blue gradient toward pan side" as RestingMovingGimbal

    [*] --> Off
    Off --> On : light.front.on
    On --> Off : light.front.off (from any inner state)

    state On {
        [*] --> Resting
        Resting --> MovingForward : movement.forward
        Resting --> MovingBackward : movement.backward
        Resting --> RestingMovingGimbal : gimbal.move

        MovingForward --> MovingForward : movement.forward
        MovingForward --> MovingBackward : movement.backward
        MovingForward --> Resting : movement.stop

        MovingBackward --> MovingBackward : movement.backward
        MovingBackward --> MovingForward : movement.forward
        MovingBackward --> Resting : movement.stop

        RestingMovingGimbal --> RestingMovingGimbal : gimbal.move, outside 80-100° and change > 5
        RestingMovingGimbal --> Resting : gimbal.move, within 80-100°
    }
```

`On` only groups the states for readability. In the code, each inner state handles `light.front.off` on its own.

### Gimbal ([`GimbalState.h`](../src/states/GimbalState.h))

```mermaid
stateDiagram-v2
    [*] --> ManualControl : pan = 90, tilt = 90
    ManualControl --> ManualControl : gimbal.move (either angle changes > 2)
    note right of ManualControl
        Angles are mapped from 0-180 to 20-160
        before they reach the servos
    end note
```

### RC monitor ([`RCState.h`](../src/states/RCState.h))

`RCMonitoringState` is not wrapped in a `StatefulController` and is not registered on the bus: it only produces events. Its constructor starts the `readRC` task, which reads the receiver and calls `dispatchEvent` directly. It lives for the whole run and must never be deleted, because the task keeps using it.

Driving modes, such as the planned autonomous driving, should be a state machine in their own controller that reacts to events. They don't belong in the RC monitor.
