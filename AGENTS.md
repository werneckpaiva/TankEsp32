# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project

Firmware for a tank robot driven by an ESP32 (`esp32dev`), written in C++ with the Arduino framework on top of FreeRTOS. Input comes from an RC receiver (FlySky iBus). Behaviour is built from an event bus and state machines, implemented in the local `EventDrivenStates` library.

## Build, flash, monitor

PlatformIO is the build system (`platformio.ini`, single env `esp32dev`).

```sh
pio run                    # compile
pio run -t upload          # flash over USB
pio device monitor         # serial console, 115200 baud
```

There are no unit tests and no CI. The only checks are "it compiles" and behaviour on real hardware. Tell the user when a change still needs hardware testing.

### Known build issue: Arduino core version

`platform = espressif32` has no version pin, so PlatformIO currently installs Arduino-ESP32 core **3.x** (seen: 3.3.11 / IDF 5.5). The code was written for core **2.x**, and on 3.x the build fails:

- `WheelsMotorDriver.h` calls `ledcSetup` / `ledcAttachPin`. Core 3.x removed both and replaced them with `ledcAttach(pin, freq, res)` and `ledcWrite(pin, duty)`.
- `ESP32Servo@^0.11.0` calls `ledcDetachPin` and also fails to compile on 3.x.

To fix this, either pin the platform to a 2.x-core release (for example `platform = espressif32@6.x`) or port both call sites to the 3.x LEDC API. Ask the user which one they want before you change `platformio.ini`.

## Layout

```
lib/EventDrivenStates/   Local library: Event, EventListener, EventBus, State, StatefulController
src/main.cpp             Pin map, object wiring, and listener registration (setup only; loop() is idle)
src/drivers/             Hardware wrappers (motors, servos/gimbal, NeoPixel strip, RC receiver, distance sensor)
src/events/              Concrete Event subclasses and their key constants
src/states/              State subclasses: one state machine per subsystem
```

Headers under `src/` are **header-only and contain non-inline definitions**. Include them only from `main.cpp` (one translation unit). If you add a second `.cpp` that includes them, you get multiple-definition link errors. If you need another `.cpp`, split the header into `.h`/`.cpp` first.

## Architecture: EventDrivenStates

Mermaid diagrams of the event flow, event lifecycle, classes and every state machine are in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Update them when you change transitions, event keys or wiring.

- **Event**: has a dotted key (for example `movement.forward`, `gimbal.move`, `light.front.on`). Each subclass must implement `getEventKey()` and `clone()`. `clone()` must deep-copy any owned memory (see `MoveGimbalEvent`, which resets its `toString` buffer in the clone).
- **EventBus**: `dispatchEvent(new X(...))` puts a pointer on a FreeRTOS queue. A dispatcher task matches each event against the listeners by **key prefix** (`strncmp`). An empty prefix `""` matches every event. Each matching listener gets its **own clone**. The bus then deletes the original.
- **EventListener**: each listener runs its own FreeRTOS task and queue. It calls `receiveEvent()` and then **deletes the event**. Never keep an event pointer after `transition()` returns.
- **StatefulController**: an EventListener that holds the current `State`. On each event it calls `currentState->transition(event)`:
  - Return `this` to stay in the current state.
  - Return a `new` state to move to it. The controller deletes the old state.
- **Entry actions live in state constructors**. For example, `StoppedState` calls `stopMoving()` and `FrontLightRestingState` paints the strip blue. Building a state therefore drives the hardware.
- Transitions compare keys with `strcmp` against the `static constexpr` key constants in `src/events/`, then cast the event to the concrete type. If you add a new event type, give it a unique key under the right prefix.
- `RCMonitoringState` is a **source**, not a reactor. Its constructor starts a `readRC` task that polls the receiver every 50 ms and dispatches events only when values change (no retransmission: RC input is continuous, so dropping an occasional event is preferred). It is created directly in `main.cpp` (`rcMonitor`), not wrapped in a `StatefulController` and not registered on the bus, because it never consumes events. Never delete it: its task keeps using the object. Future driving modes (e.g. autonomous driving) belong in their own controller, not in the RC monitor.
- `EventBus` guards its listener list with a mutex (`listenersMutex`): the dispatcher task walks it while `addEventListener` / `removeEventListener` may run from other tasks. Never call those two from inside the dispatcher. `removeEventListener` unlinks every prefix of a listener but does not delete the listener.

### Adding a subsystem

1. Write a driver in `src/drivers/`.
2. Define its events in `src/events/` with a common key prefix.
3. Write its states in `src/states/`: a base state holding the driver, concrete states, and their transitions.
4. In `main.cpp`, create the driver and a `StatefulController(new InitialState(eventBus, driver))`, then call `eventBus->addEventListener("<prefix>.", controller)`.

## Current wiring (`src/main.cpp`)

The RC monitor (`rcMonitor`, an event source) and three controllers are active: movement (`"movement."`), gimbal (`"gimbal."`) and front lights. The front-lights controller is registered with prefix `""` because it reacts to movement, gimbal and light events.

| Function | GPIO |
|---|---|
| Motor 1 A/B | 18 / 19 |
| Motor 2 A/B | 22 / 23 |
| Gimbal pan / tilt servo | 25 / 26 |
| Front NeoPixel strip (8 px, GRB) | 27 |
| Distance sensor echo / trigger | 35 / 32 (driver declared only, not implemented) |
| RC iBus receiver | `Serial2` (default RX2 = GPIO16) |

RC channels: ch0 = turn (-255..255), ch1 = throttle (-255..255), ch2 / ch3 = gimbal tilt / pan (0..180, inverted), ch4 = lights switch.

## Conventions and gotchas

- **Debug output:** never call `Serial.print*` directly. Use `DEBUG_PRINTF(...)` / `DEBUG_PRINTLN(msg)` (defined in `EventDrivenStates.h`). They compile to nothing, arguments included, unless `DEBUG_MODE` is defined. It is set in `platformio.ini` (`build_flags = -D DEBUG_MODE`) and applies to `src/` and `lib/`. Code that exists only for debugging, such as the `printStatus` task, goes inside `#ifdef DEBUG_MODE`.
- Code style: 2- or 4-space indentation (it varies by file), `this->` everywhere, explicit getters, `#ifndef X_h` include guards, and `// STATES ###` / `// Transitions ###` section banners in state headers. Match the file you are editing.
- `src/states/FrontLighstState.h` has a typo in its filename (`Lighst`). Keep the existing name unless the user asks you to rename it.
- `FrontLighstState.h` uses `MovementEvent` and `MoveGimbalEvent` but doesn't include their headers. It compiles only because `main.cpp` includes those headers first. Keep that include order, or add the includes.
- Several `FrontLightsState`, `StoppedState` and `MovementState` paths have small bugs. For example, `StoppedState` passes its uninitialized members to the base constructor. Fix only what the task calls for, and mention any others you notice.
- Memory is tight and everything is heap-allocated. Every listener costs a task (3 KB stack by default) plus a queue (3 events by default). If a listener queue is full, the dispatcher drops the event for that listener immediately. The deepest listener path is `Serial.printf` (newlib `_svfprintf_r` alone uses 784 bytes), so keep formatted logging, especially `%f`, out of listeners or raise their stack. In debug builds, `printStatus` in `main.cpp` logs heap usage and each listener's minimum free stack every 2 s.
- Arduino libraries come from `lib_deps` (IBusBM, ESP32Servo, Adafruit NeoPixel). Don't vendor them, and don't edit anything under `.pio/`.
