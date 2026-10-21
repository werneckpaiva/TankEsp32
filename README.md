# TankEsp32

Event-driven firmware for a small RC tank robot (about 15–16 cm long), driven by an ESP32, plus the 3D-printed pan/tilt camera head that goes on top of it.

- **Firmware:** C++ on the Arduino framework and FreeRTOS, built with PlatformIO (`esp32dev`).
- **Input:** a FlySky RC receiver over iBus.
- **Behaviour:** an event bus and state machines, implemented in the local `EventDrivenStates` library.
- **Camera head:** a Wall-E style gimbal modelled in build123d, in [`3d-model/`](3d-model/AGENTS.md).

## Hardware

| Function | GPIO |
|---|---|
| Motor 1 A/B | 18 / 19 |
| Motor 2 A/B | 22 / 23 |
| Gimbal pan / tilt servo | 25 / 26 |
| Front NeoPixel strip (8 px, GRB) | 27 |
| Distance sensor echo / trigger | 35 / 32 (driver declared only, not implemented) |
| RC iBus receiver | `Serial2` (default RX2 = GPIO16) |

RC channels:

| Channel | Use | Range |
|---|---|---|
| 0 | Turn | -255..255 |
| 1 | Throttle | -255..255 |
| 2 | Gimbal tilt | 0..180 (inverted) |
| 3 | Gimbal pan | 0..180 (inverted) |
| 4 | Front lights switch | on / off |

## Build, flash, monitor

Install [PlatformIO](https://platformio.org/), then:

```sh
pio run                    # compile
pio run -t upload          # flash over USB
pio device monitor         # serial console, 115200 baud
```

There are no unit tests and no CI. A change is verified by compiling it and by running it on the tank.

`platformio.ini` sets `-D DEBUG_MODE`, which turns on `DEBUG_PRINTF` / `DEBUG_PRINTLN` output and the `printStatus` task (heap and listener stack usage every 2 s). Remove the flag for a build without debug output.

### Known build issue: Arduino core version

`platform = espressif32` is not pinned, so PlatformIO now installs Arduino-ESP32 core **3.x**. The code was written for core **2.x**, and on 3.x the build fails:

- `WheelsMotorDriver.h` calls `ledcSetup` / `ledcAttachPin`, which 3.x replaced with `ledcAttach`.
- `ESP32Servo@^0.11.0` calls `ledcDetachPin` and does not compile on 3.x.

The fix is either to pin a 2.x-core platform (for example `espressif32@6.x`) or to port both call sites to the 3.x LEDC API. Neither has been done yet.

## How it works

One component, `RCMonitoringState`, polls the receiver every 50 ms and publishes events to an `EventBus` when channel values change. Each subsystem has a `StatefulController` that receives the events whose key matches its prefix, runs a state machine, and drives its hardware through a driver.

| Controller | Event prefix | Driver | Does |
|---|---|---|---|
| `movementController` | `movement.` | `WheelsMotorDriver` | forward, backward, spin left/right, stop |
| `gimbalController` | `gimbal.` | `GimbalDriver` | pan/tilt servos |
| `frontLightsController` | `""` (all events) | `LightsStripDriver` | strip colour and brightness follow lights switch, movement and gimbal events |

Events are heap-allocated and short-lived. The bus gives each matching listener its own clone, and each listener runs in its own FreeRTOS task with its own queue. Entry actions live in state constructors, so building a state drives the hardware.

The event flow, event lifecycle, class diagram, event keys and every state machine are in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Project layout

```
lib/EventDrivenStates/   Local library: Event, EventListener, EventBus, State, StatefulController
src/main.cpp             Pin map, object wiring and listener registration (setup only; loop() is idle)
src/drivers/             Hardware wrappers (motors, servos/gimbal, NeoPixel strip, RC receiver, distance sensor)
src/events/              Concrete Event subclasses and their key constants
src/states/              State subclasses: one state machine per subsystem
docs/                    Architecture diagrams (Mermaid)
3d-model/                The camera head gimbal: build123d model, tests, STLs, 3MFs, assembly guide
gimbal.sh                Shortcut for the gimbal model tasks
AGENTS.md                Guidance for AI coding agents working in this repo
```

Headers under `src/` are header-only and contain non-inline definitions, so include them only from `main.cpp`. A second `.cpp` that includes them causes multiple-definition link errors.

### Adding a subsystem

1. Write a driver in `src/drivers/`.
2. Define its events in `src/events/` with a common key prefix.
3. Write its states in `src/states/`: a base state holding the driver, concrete states, and their transitions.
4. In `main.cpp`, create the driver and a `StatefulController(new InitialState(eventBus, driver))`, then call `eventBus->addEventListener("<prefix>.", controller)`.

Memory is tight: every listener costs a task (3 KB stack by default) plus a queue (3 events by default). If a listener's queue is full, the dispatcher drops the event for that listener.

## Camera head gimbal

A 3D-printed pan/tilt head for the tank, printed on a Bambu Lab A1 in PLA. It carries three things that aim together:

- an ESP32-S3-CAM board (camera and web server);
- an HC-SR04 ultrasonic sensor, whose two cans are the eyes;
- an SYD1230 laser pointer in a clamp on top.

Two MG90S servos give pan of ±90° and tilt from -45° (down) to +90° (up). Both axes run on 608 bearings, so the servo shafts do not carry the head's weight. The base plate has the footprint and M2 hole pattern of a reference gimbal and screws to the tank cover. Everything connects with Dupont jumpers, with no soldering.

The model is in [`3d-model/`](3d-model/AGENTS.md): every dimension is in `python/params.py`, and about 190 geometric tests check clearances, printability and the motion range. The generated STLs, 3MFs and assembly guide are git-ignored and are rebuilt with `gimbal.sh`:

```sh
./gimbal.sh viewer         # start the OCP viewer at http://localhost:3939
./gimbal.sh build          # motion checks, write the STLs, show the assembly
./gimbal.sh build --pan 45 --tilt -30   # show another pose
./gimbal.sh 3mf            # build the Bambu Studio projects (needs Bambu Studio)
```

It needs a Python with `build123d`; install `3d-model/requirements.txt` into a `.venv`, or point `$PYTHON` at one. Tests run from `3d-model/python/` with `python -m pytest tests -q`. See [3d-model/AGENTS.md](3d-model/AGENTS.md) for the design, the parts list, the print settings and the open questions.

The head has its own ESP32 (the camera board), separate from the tank's. The two talk over a serial link. The firmware in this repo drives the servos on GPIO 25/26 and does not yet use the head's HC-SR04 or laser.

## Status and plans

- The RC monitor, movement, gimbal and front-lights controllers are working.
- The distance sensor driver is declared but not implemented.
- Autonomous driving is planned. It will be a state machine in its own controller that reacts to events, not part of the RC monitor.
- Several states have small known bugs (for example `StoppedState` passes uninitialized members to its base constructor).

## For AI coding agents

Read [AGENTS.md](AGENTS.md) for this firmware and [3d-model/AGENTS.md](3d-model/AGENTS.md) for the gimbal model. Update [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) when you change transitions, event keys or wiring.
