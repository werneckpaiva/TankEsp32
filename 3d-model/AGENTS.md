# AGENTS.md: Wall-E camera head gimbal

Context for any coding agent working in this folder: what the design is for,
how it is built today, and how to work on it. Read this first, then
`params.py` and the module docstrings. Last updated 2026-10-21.

This file merges the old `DESIGN.md` (the original spec approved on
2026-10-20) with the working notes. Where the build differs from the spec, this
file describes the build; the reasons are in "Design decisions and how they
evolved". Older documents (`docs/superpowers/plans/…`, `progress.md`) still
cite `DESIGN.md` and its section numbers. Those sections now live here.

## What this is

A 3D-printed pan/tilt "moving head" for a small RC tank (about 15–16 cm long).
The user (Ricardo) designs it here in build123d and prints it on a Bambu Lab A1.
It should look like a small Wall-E style robot head, not a bare bracket.

- **The head** carries three things that aim together:
  - an ESP32-S3-CAM board (camera, web server);
  - an HC-SR04 ultrasonic sensor, whose two cans are the "eyes", Wall-E style;
  - an SYD1230 laser pointer (Ø12 mm) in a clamp on top.
- **Motion:** two MG90S servos, pan ±90° and tilt −45° (down) to +90° (up).
  Both axes run on 608 bearings (8 × 22 × 7; the user has five).
- **Mounting:** the base plate keeps the footprint and M2 hole pattern of a
  reference gimbal (`3mf/reference/gimbal.3mf`,
  [MakerWorld 511916](https://makerworld.com/en/models/511916-sg90-servo-2-axis-gimbal),
  a remix of [Thingiverse 2892903](https://www.thingiverse.com/thing:2892903))
  and screws to the tank cover, which is a separate model. It replaces that
  gimbal and fixes its weaknesses: it was an open bracket, had no room for
  electronics or wiring, and its servo shafts carried all the load.
- **Electronics:** a second ESP32 on the tank drives the servos, sensor, laser,
  motors and RC. The two ESP32s talk over a bidirectional serial link. The
  camera ESP32 streams video over a web server and receives commands. Only
  wires go up into the head; no other electronics live in the gimbal.
- **Wiring:** everything connects with Dupont jumpers. **No soldering.**
- **Use:** at rest the head looks straight ahead, level with the floor. The
  exact servo angles for "straight ahead" are calibrated later in software, so
  the tilt servo's travel does not have to be centred on level.

## Goals, non-goals, anti-goals

**Goals**
- Pan about ±90° (the full servo travel); tilt about 45° down to about +90°
  (straight up), with no collisions anywhere in that range.
- Camera, HC-SR04 and laser move together and point the same way.
- Base plate matches the reference gimbal's footprint and screw holes.
- Robust enough for a tracked vehicle: no wobble, and no servo shaft carrying
  the head's weight sideways.
- USB-C on the camera board stays reachable for reflashing without taking
  anything apart.
- The microSD card can stay inserted and can be removed without disassembly.
- Prints on the A1 (0.4 mm nozzle) in PLA, with minimal supports.

**Non-goals**
- Continuous rotation or a slip ring (±90° pan is enough for a wire loop).
- An external Wi-Fi antenna (the board keeps its onboard antenna).
- Weatherproofing.
- Firmware and the main ESP32's electronics (only the notes under "Wiring").
- The tank's cover. This design only provides the base plate that screws onto it.

**Anti-goals** (these count as failure even if everything technically moves)
- The head wobbles or sags because the servo shafts take bending loads.
- Panning or tilting pulls or snags wires, or unplugs a Dupont connector.
- Reflashing or swapping the SD card requires opening the head.
- Any part (eyes, laser, head shell) collides with the arms, yoke or neck
  inside the required range.
- It looks like a bare bracket instead of a head, or is out of scale for a
  16 cm tank.

## Working with this user

- **Do exactly the change asked.** If they say "just enable X", do only that.
  Mention any deeper issue in one line and ask before acting.
- **Measurements:** they measure real parts with calipers and send photos. Put
  measurements in `params.py` with a comment saying *measured*; anything
  guessed says *estimate*.
- **After every geometry change:**
  - regenerate the STLs, both 3MFs and the guide;
  - tell them **which parts to reprint**, by comparing the new STLs with the
    meshes in the last 3MF they printed. Unchanged parts must not be reprinted.
- **Fit tests:** they like a quick test print before a full part. Keep
  `gimbal_fit_test` in sync (it is cut from the real head front).
- **They print with:** a Bambu A1, 0.4 mm nozzle, 0.16 mm High Quality, Bambu
  PLA Matte, textured PEI plate.

## Files

```
3d-model/
  AGENTS.md   this file
  python/     the model, its tests and tools (run everything from here)
  stl/        generated STLs, one per printed part
  3mf/        generated Bambu Studio projects, plus printed/ and reference/
  docs/       assembly guide, its drawings, the board datasheet, old plans
```

| File | Role |
|---|---|
| `python/params.py` | **Every dimension.** Board, sensor, servo, horn, bearings, base, fits, wires. Change measurements here only. |
| `python/components.py` | Reference models of the bought parts, plus keep-out volumes (`esp32_keepout`, `sd_access`, `usb_plug`, `hcsr04_keepout`, …) that the tests check the printed parts against. |
| `python/base.py` | Base plate (reference footprint) + round drum neck holding the pan servo. Also holds the pan "stack" heights. |
| `python/pan.py` | Neck cap (pan 608 seat, wire slot), pan coupler (horn pocket + stub shaft), printed bushing fallback. |
| `python/yoke.py` | Yoke: crossbar + −X arm housing the tilt servo; `make_pin_arm()` is the separate +X arm with the tilt 608. The tilt-axis height is derived from the head's swept size. |
| `python/head.py` | Head front shell, rear cover, brow tubes, tilt axle pin, fit-test piece. `face_mounts()` / `face_openings()` are shared by the head and the fit test. |
| `python/gimbal_head.py` | Entry point. Its docstring is the **user guide**: parts, hardware list, assembly steps, viewing, printing. Also has `place(pan, tilt)`, motion checks, STL export, the viewer, and `--pan/--tilt` arguments. Defines the output folders (`STL_DIR`, `THREEMF_DIR`). |
| `python/make_3mf.py` | Builds `3mf/gimbal_head.3mf` (all parts) and `3mf/gimbal_fit_test.3mf` from `stl/`, with the print settings embedded, then slices them through the Bambu Studio CLI. |
| `python/tools/guide/` | `stages.py` and `tilt_exploded.py` draw SVGs into `docs/drawings/`; `make_guide.py` builds `docs/ASSEMBLY_GUIDE.pdf`. The guide text lives in `make_guide.py`. |
| `python/tools/compare_parts.py` | Lists which parts changed since a printed 3MF, for the "what to reprint" answer. |
| `python/tests/` | pytest, about 190 geometric tests (`conftest.py` and `pytest.ini` sit in `python/`). |
| `stl/gimbal_*.stl` | Generated by `gimbal_head.py`. |
| `3mf/gimbal_head.3mf`, `3mf/gimbal_fit_test.3mf`, `3mf/result.json` | Generated by `make_3mf.py` (`result.json` is the slicer's report). |
| `3mf/printed/` | Copies of 3MFs that were sent to the printer, as baselines for `compare_parts.py`. |
| `3mf/reference/gimbal.3mf` | The reference gimbal from MakerWorld. |
| `docs/ASSEMBLY_GUIDE.pdf`, `docs/drawings/` | Generated assembly guide and its SVGs. |
| `docs/Sd8830c6….pdf` | Board datasheet (a GitHub README printout). |
| `docs/superpowers/plans/2026-10-20-gimbal-head.md` | Original implementation plan. Its "§n" references point to the old `DESIGN.md`, now merged here, and its paths predate the folder layout. |
| `.superpowers/sdd/2026-10-20-gimbal-head/progress.md` | Running ledger of every change and design ruling, with reasons. Read it for history. |
| `.superpowers/brainstorm/*/content/layout-v4.html` | Layout mockups from the design session (v4 is the latest). |

The generated outputs (`stl/`, the two generated 3MFs, `result.json`, the
guide PDF and `docs/drawings/`) are git-ignored. After a fresh clone, rebuild
them with the commands below. `3mf/printed/` and `3mf/reference/` are tracked.

## Commands (run from `python/`)

The user's shortcut is `../gimbal.sh` in the TankEsp32 root: `viewer` (start
the OCP viewer), `build [--pan N --tilt N]` (runs `gimbal_head.py`) and `3mf`
(runs `make_3mf.py`). It finds the interpreter from `$PYTHON`, then a `.venv`
in `3d-model/` or the root, then `python3`.

`python` below means `../../.venv/bin/python`: the TankEsp32 root `.venv`
(Python 3.14) with build123d 0.13.0, ocp-viewer, pytest, reportlab and
svglib installed (pinned in `3d-model/requirements.txt`).

```bash
python -m pytest tests -q            # all tests, about 75 s
python gimbal_head.py                # motion checks + all STLs + fit-test STL (to ../stl) + viewer
python gimbal_head.py --pan 45 --tilt -30   # show another pose
python make_3mf.py                   # ../3mf/gimbal_head.3mf + gimbal_fit_test.3mf (needs /Applications/BambuStudio.app)
python tools/guide/stages.py && python tools/guide/tilt_exploded.py \
  && python tools/guide/make_guide.py   # ../docs/ASSEMBLY_GUIDE.pdf
python tools/compare_parts.py ../3mf/printed/<last printed>.3mf ../stl   # what to reprint
```

- **Viewer:** start `../../.venv/bin/ocp-viewer` (or `../gimbal.sh viewer`), then open
  http://localhost:3939. Without it, `gimbal_head.py` logs viewer errors and
  still exits 0.
- **Order after a change:** tests → `gimbal_head.py` (writes the STLs) →
  `make_3mf.py` (reads the STLs) → guide.

## Conventions

- **Units are mm.** Values are written as `n * MM`.
- **World frame:**
  - origin on the pan axis at the bottom of the base plate;
  - +Y forward (the camera's view direction at rest), +Z up, +X to the right
    seen from behind;
  - positive pan turns toward +X, positive tilt looks up.
- **Head frame:** origin on the tilt axis, same axes at rest.
- **Sides:** the **SD card side is +X**, which is the viewer's *left* when
  facing the camera. The tilt servo is on −X; the slim pin arm and its bearing
  are on +X.
- **Board positions in `params.py`:** measured from the board's top-left
  corner *as seen from the front*, board upright, USB-C at the bottom. Convert
  with `components.board_x()` and `board_z()`. Watch the mirror: from the front,
  "left" is +X.
- **Code style:** like `../tv/ir_remote_case.py`. `from build123d import *`, a
  comment on each non-obvious constant, module docstrings that explain frames
  and assembly.
- **Imports:** modules use `import params as p` (never `from params import`)
  so tests can patch and reload. Dependency order: params → components → base →
  pan → head → yoke → gimbal_head. **yoke imports head**, never the other way
  round.
- **TDD:** write the geometric test first, watch it fail, then change the
  model. Typical tests:
  - `is_inside` probes;
  - `(a & b).volume < 0.01` (no overlap);
  - `distance_to` (clearance);
  - keep-out volumes;
  - slicing checks for floating starts and steep overhangs (helpers in
    `tests/test_export.py`).
- **Motion checks:** the head is swept through the tilt range at pan −90/0/+90.
  There must be no overlap and at least 0.5 mm clearance (`MOVE_CLR`) outside
  the intended joints (`joint_zone`).
- **Printability is tested:**
  - each printed part is a single solid;
  - it rests flat on the bed (more than 50 mm² of contact);
  - parts printed without supports have almost no overhang beyond 45°;
  - the base has no floating starts.
- **Left to the builder** (no need to ask): how parts split and join, screw
  sizes (M2 by default, matching the base and servo screws), exact pivot
  positions as long as the ranges and clearances hold, styling (fillets, brow
  size, taper) as long as it reads as a compact robot head, print orientation
  and supports, and fit tolerances (0.2–0.3 mm clearance by default).

## Layout

Schematic front view (not to scale):

```
            ┌──[laser]──┐          ← SYD1230 in a clamp on top, centred
        ╭───┴───────────┴───╮
        │  (( O ))   (( O )) │     ← HC-SR04 cans = eyes, inside brow tubes
        ╰─╮               ╭─╯
 pin arm ─┤ SD   =O=      ├── tilt-servo arm
   (slim, │   ESP32-S3-   │   (servo inside, −X)
    +X)   │      CAM      │
          │  (B) USB (R)  │     ← head tapers around the upright board
          ╰───────────────╯
     ═══════════ yoke ═══════════   ← pans with the head
            ╭─────────╮
            │  drum   │            ← round neck, hides the pan servo
            │  neck   │
          ▄▄▄▄▄▄▄▄▄▄▄▄▄              ← base plate, 41.8 × 30.8, screws to the tank cover
```

The original envelope target was about 72 mm wide (arm to arm), head about
52 mm wide at the eyes and 110–125 mm tall including the laser. These were
targets, not limits; the current size is under "Current state".

## Parts and mechanics

### Base plate and neck (fixed)

- **Base plate** (measured from `3mf/reference/gimbal.3mf`, part "base"):
  - footprint **41.8 × 30.8 mm**, corner-rounded;
  - 4 × **Ø2.2 mm** (M2) holes on a **33 × 22 mm** pattern (±16.5, ±11 from
    centre), with **Ø4.4 mm counterbores 2.2 mm deep** from the top. The
    corner bosses are 4.4 mm tall; the rest of the plate is about 2.2–2.6 mm
    thick;
  - a cable pass-through near the centre, inside the hole pattern (the
    reference's is about 7.5 × 9.6 mm), big enough for the whole bundle;
  - the pan axis is at the plate centre. Which way the long side runs relative
    to the tank's forward direction is a single parameter.
- **Neck:** a round drum (Ø48.7 mm) printed with the plate. It flares out and
  overhangs the plate to clear the MG90S tabs and the horn coupler's sweep;
  the plate footprint and holes are unchanged.
- **Pan servo:** stands vertically in the drum, shaft up on the pan axis,
  screwed by its tabs to the front pillar and the rear ledge. Its cable leaves
  the **shaft end**, runs under an arch in the front pillar and goes straight
  down into the tank.

### Pan joint

- **Load path:** the 608 sits in the neck cap (screwed to the drum, 4 × M2 ×
  16). The pan coupler holds the servo's supplied plastic horn in a pocket;
  its stub goes up through the bearing into a keyed socket in the yoke,
  fixed with an M2 screw. The yoke's crossbar rests on the bearing's inner
  ring. Vertical and tipping loads go through the bearing into the neck; the
  servo only turns the head.
- **Never print a spline.** Horns are always the servo's own, captured in a
  printed pocket.
- **Wires** cross the pan joint at `WIRE_ANGLE` (−X) through holes that turn
  with the yoke and an arc slot in the cap sized for the ±90° sweep, beside the
  bearing, not through its bore.

### Yoke (pans)

- **−X arm** (opposite the SD card, can be chunky): houses the tilt servo,
  shaft inward on the tilt axis. The servo slides in from outside and its tabs
  screw to the arm's inner wall. Its cable goes down the arm into the yoke and
  then the neck; it never enters the head.
- **+X arm** (`pin_arm`, SD side): slim, a separate part bolted to the
  crossbar (2 × M3 × 12 from below). It ends just above the pivot so it doesn't
  cover the SD slot, and holds the tilt 608.
- The arms stand outside the head's widest part (the eye section), so the head
  tilts through its whole range without meeting them. The tilt-axis height is
  derived from how far the head reaches below the axis over that range.

### Tilt joint

- **−X:** the tilt servo's horn sits in a pocket on the head's side.
- **+X:** the printed axle pin goes through the 608 in the pin arm into a
  socket in the head, clamping the inner ring against a collar with an M3 × 25
  bolt, nut inside the head.
- **Pivot location:** near the head's centre of mass, so a small servo holds
  it without strain, and placed so the full −45° … +90° sweep clears the yoke
  and neck. The laser and the eyes are the parts most likely to collide.

### Bearings

- Each bearing is a `Bearing(bore, od, width)` in `params.py`; seats and shafts
  derive from it. A larger pan bearing (e.g. 6805, 25 × 37 × 7) should work
  with the same layout and a fatter stub. The tilt axle is a printed pin, so
  the tilt bearing's bore must be at least 6 mm.
- `USE_PAN_BEARING` / `USE_TILT_BEARING = False` replaces a bearing with a
  printed bushing of the same envelope, so parts can be printed before the
  bearings arrive.

### Head (tilts)

Wider at the top (the eye section, set by the HC-SR04 width), tapering to a
narrower body around the board. Rounded edges throughout, Wall-E inspired but
not a copy. Printed as a front shell (face, eyes, camera openings, board
mounts, laser clamp, side joints), a rear cover and the brow tubes.

- **Eyes:** the HC-SR04 slides in from the back and is screwed (4 × M2 × 6
  through its Ø2 holes) to four corner posts joined to the walls. Its cans pass
  through the eye openings and stand out 1.5 mm (`CAN_OUT`) inside the brow
  tubes, which plug into the openings from outside.
- **Laser:** in a split-ring clamp on top, centred left-right and parallel to
  the camera's axis, pinched by an M2 × 10. The tube can slide and rotate so
  the dot can be aligned with the image centre.
- **Camera board:** stands upright (portrait) facing forward, USB-C at the
  bottom, 4.8 mm behind the face (`FACE_GAP`), so the lens pokes out about
  0.6 mm. Pinned at two diagonal corners, screwed (M2 × 6) at the other two.
  Never clamp it by its header pins. Seen from the front, the board has:
  - top row: SD slot (top-left), flash LED, camera (centred), flash LED; the
    onboard antenna is on the top edge;
  - bottom: USB-C centred, BOOT (left) and RESET (right) beside it;
  - header rows down the left and right edges, pins out the back.
- **Face openings:** the **=O=** (a Ø12.5 round hole that just clears the
  square camera block, with slots for the two flash LEDs, 1 mm margin), the
  eye openings, and a window for the status LED with a light path cut through
  the top-left standoff.
- **Access without opening the head:**
  - USB-C: an opening in the bottom that fits a typical cable plug overmold
    (tilting the head up a bit for access is fine);
  - BOOT/RESET: pinholes for a toothpick;
  - SD card: it enters from the board's left edge (as seen from the front, +X)
    and sticks out a little; a slot in the +X side wall lets a fingernail push
    and pull it. That's why the pin arm stops below it.
- **Dupont bay:** the depth behind the board takes the header pins (8.5 mm
  with the spacer), the straight Dupont housings (14 mm) and the wire bend;
  the same behind the HC-SR04's pins. Wires gather at the bottom rear and
  leave near the tilt axis, so tilting doesn't stretch them.
- **Rear cover:** has a locating lip, two M2 screws at the bottom from behind
  and two from above through the top wall. The electronics go in and the
  wires plug in with the cover off.

## Component reference data

All of these are named parameters in `params.py`.

| Component | Key dimensions | Confidence |
|---|---|---|
| ESP32-S3-CAM PCB | 38.4 × 30.4 mm; 4 holes on a 32 × 24 mm pattern, 3.2 mm from the edges | measured (and datasheet) |
| Camera lens | position and diameters 7.94 / 7.0; tip 7.05 mm above the PCB | measured |
| Camera block | `CAM_MODULE` 8.5 mm wide; `CAM_BLOCK_H` front at lens tip − 1 mm | **estimate** |
| Flash LEDs | 2 mm, at 9.0 and 23.4 mm from the left; `LED_Y` 6.5 mm from the board top | measured / `LED_Y` **estimate** |
| Status LED | centre at (6, 3) mm | measured |
| USB-C | 3.25 mm tall, centred on the bottom edge, overhangs the PCB slightly | measured |
| SD socket | 3.2 mm tall, about 10.5 mm wide shell at top-left; card sticks out past the left edge | measured height |
| HC-SR04 | 45 × 20 mm; cans Ø16, 26 mm apart; holes Ø2; 4 pins at the bottom-edge centre | measured |
| HC-SR04 details | `SR_HOLE_INSET` 1.6 mm (hole centres from edges); `SR_TX_H` 12 mm can height | **estimate** |
| SYD1230 laser | Ø12 × about 35 mm, 2 wires | Ø measured, length from listings |
| MG90S servo (both axes) | body about 22.8 × 12.2 × 22.7; tabs 32.3 overall; shaft about 6 mm from one end; metal spline (`SERVO_*`) | **estimate** |
| MG90S horn | supplied plastic horn (`HORN_*`) | **estimate** |

Measure the estimates if fit problems appear. Keep the measured values.

## Wiring

Wires that go up into the head, all with Dupont terminals:

| From | Wires |
|---|---|
| ESP32-S3-CAM | 5V, GND, TX, RX |
| HC-SR04 | VCC (5V), GND, Trig, Echo |
| Laser | +, − |
| Tilt servo | 3-wire cable (starts in the yoke arm, doesn't enter the head) |

- Up to 10 wires leave the head near the tilt axis, then with the tilt servo
  cable (13 in all) run through the yoke into the neck and out the base
  pass-through. Power and ground may be shared, but the design must allow the
  full count.
- Pan is ±90°, so a slack loop near the pan axis is enough, in a defined path
  so it can't get caught between moving and fixed parts.
- Dupont plugs connect inside the head and at the main ESP32. Only bare jumper
  wires and the servo plug (`PLUG_W`) need to pass the neck and base holes; if
  that's tight, they must at least fit one at a time.

**Electronics notes** (outside this design, for the user):
- **HC-SR04 Echo is a 5 V signal.** Put a divider (e.g. 1 kΩ / 2 kΩ) on the main
  ESP32's input, on a breadboard or with inline Dupont parts.
- **Laser:** about 30–40 mA. Switch it with a small transistor or MOSFET module,
  not straight from a GPIO.
- **Servos:** their own 5 V supply good for about 1 A, not the ESP32's 3.3 V or
  USB pin, with ground shared.

## Current state of the design (2026-10-21)

**Overall:**

| | |
|---|---|
| Size | about 83 × 49 × 146 mm (width × depth × height) |
| Tilt axis height | 72.4 mm |
| Neck drum | Ø48.7 mm |
| Head depth | 38.7 mm |
| `gimbal_head.3mf` | one plate, about 5.1 h, 79 g PLA |
| `gimbal_fit_test.3mf` | about 50 min, 12 g |

**Printed parts and their print orientation:**

| Part | Orientation | Supports / brim |
|---|---|---|
| base | upright | **supports** (user's request) |
| neck_cap | upside down | none |
| pan_coupler | as is | none |
| yoke | lying on the −X arm's outer face | **supports + brim** |
| pin_arm | on its outer face | none |
| head_front | face down | none |
| head_rear | back face down | none |
| brows | tube end down | none |
| tilt_axle | flange down | **brim** |

- **Print settings in both 3MFs:** nozzle 210 °C (first layer 220 °C), "avoid
  crossing walls" on.
- **Stringing:** the user has had stringing problems. Drying the filament was
  recommended.

**What the user has printed:** the full set from an earlier 3MF, plus fit tests.

**Still to reprint after the latest changes:** `head_front`, `head_rear`,
`brows`. Check with `tools/compare_parts.py` against the newest file in
`3mf/printed/`.

`3mf/printed/2026-10-21_round_lens_window.3mf` is the 3MF from before all of
2026-10-21's head changes:
- the head still had the round lens window and a 5.5 mm face gap;
- the HC-SR04 sat on ribs.

Since then, all of these changed: the visor and then the =O=, the cans through
the face, the corner posts, the axle boss, the board screws and the cover lip.
Ask the user to drop each 3MF they actually print into `3mf/printed/`.

## Open questions (waiting on the user)

- **Head depth:** they find the head too deep (38.7 mm). It's set by the
  Dupont plugs on the board's back: header pins 8.5 + straight housings 14 +
  wire bend. Options offered:
  - trim to the minimum for straight plugs (about 2.5 mm shallower);
  - use 90° Dupont connectors on the few pins used (about 12 mm shallower).

  Either way the yoke changes too, because the tilt-axis height is derived from
  the head. **Not decided.**
- **Overall height (about 146 mm)** is above the original 110–125 target.
  Sinking the pan servo through the plate into the tank cover was offered; it
  needs a cutout in the cover. **Not decided.**

## Design decisions and how they evolved

**Calls made during the original design** (not explicitly confirmed by the user):
- MG995 rejected as too big for a 16 cm tank; the user confirmed **MG90S** for
  both axes.
- **Tilt servo in the yoke arm**, not in the head: lighter, better balanced,
  its cable doesn't flex inside the head, and the head is easier to open.
- **Servo-side arm opposite the SD card**, with a slim pin arm on the SD side.
- **Adjustable laser clamp** (slide/rotate) to align the dot with the camera.
- Pan axis at the base plate centre.

**Changes since the spec was approved:**
- **Neck:** a round drum, not a narrow "stocky column". It has to clear the
  servo tabs and the horn coupler's sweep.
- **Bearings:** 608 on **both** axes, not 623 for tilt. The tilt axle became a
  printed pin plus an M3 bolt, instead of a screw into a boss.
- **Pan coupler:** the horn pocket and stub are a separate part keyed into the
  yoke, rather than a stub on the yoke itself.
- **Yoke:** the slim +X arm is a separate bolted part (`pin_arm`), so the yoke
  prints with less support.
- **Servo-side load sharing:** the spec asked for the head to ride on a printed
  ring around the tilt horn so the servo shaft isn't the only support on −X.
  The current `head.py` / `yoke.py` have only the horn pocket on that side.
- **Wires:** they cross the pan joint on the −X side (`WIRE_ANGLE` = 180°), not
  the front.
- **Camera opening:** went from a round hole to a visor to the =O=. The board
  sits closer to the face than first designed.
- **Board mounting:** the spec suggested standoffs or pins at all four holes;
  it's now two pins plus two M2 screws.
- **Dupont bay:** the spec asked for about 30 mm of free depth behind the board.
  Whether to shrink it is an open question (see above).
- **HC-SR04 mounting:** the sensor has always slid in from the back. First its
  cans rested on the inside of the face, then on small ribs, then the cans
  were brought through the face. It's now screwed to corner posts; the thin
  pegs on the rear cover are gone.
