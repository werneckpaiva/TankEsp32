# Wall-E Camera Head Gimbal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Parametric build123d model of a pan/tilt Wall-E style camera head (ESP32-S3-CAM + HC-SR04 + SYD1230 laser on MG90S servos with bearings), with geometric self-checks, STL export per printed part and an OCP viewer preview.

**Architecture:** One parameter module feeds small modules, one per printed sub-assembly (base/neck, pan bearing parts, yoke, head). Each module builds parts in its own local frame and publishes `Location`s for the components it holds. `gimbal_head.py` composes everything with `place(pan, tilt)`, runs the collision checks, exports STLs and shows the assembly. Reference models of the bought parts double as keep-out volumes for the tests.

**Tech Stack:** Python 3 in `/Users/ricardo/Projects/3D/build123d/.venv`, build123d 0.13, ocp_viewer, pytest (installed in Task 1).

**Spec:** `esp32s3cam/DESIGN.md` (read it first; section numbers below refer to it).

## Global Constraints

- Units are mm. World frame: origin on the pan axis at the bottom face of the base plate. +Y is forward (the camera's look direction at pan 0 / tilt 0), +Z is up, and +X is to the right as seen from behind the tank.
- **The SD card side is +X.** The card is on the viewer's left when facing the camera, which is the head's right from behind. So the slim pin arm (with tilt bearing) is at +X and the tilt-servo arm is at −X.
- Base plate: 41.8 × 30.8 mm. 4 × Ø2.2 holes on a 33 × 22 pattern (±16.5, ±11). Ø4.4 counterbores 2.2 deep from the top. Corner bosses are 4.4 tall.
- Motion: pan −90…+90°, tilt −45° (down) … +90° (up) from level, with no collisions and ≥ 0.5 mm clearance between moving and static parts.
- Servos: MG90S on both axes. They're driven through their supplied plastic horns in printed pockets. **No printed splines.**
- Bearings: `Bearing(bore, od, width)`. Defaults: pan 608 = (8, 22, 7), tilt 623 = (3, 10, 4) with an M3 screw axle. `USE_PAN_BEARING` / `USE_TILT_BEARING` switch each one to a printed bushing of the same envelope.
- ESP32-S3-CAM stands upright (portrait), facing +Y, with USB-C toward −Z. Header pins point backward (−Y), and a ≥ 30 mm Dupont bay sits behind the PCB.
- Every component dimension is a named constant in `params.py`. Nothing is hard-coded elsewhere.
- Code style matches `tv/ir_remote_case.py`: `from build123d import *`, values written as `n * MM`, a comment on each non-obvious constant, and a docstring explaining frames, parts, viewing and printing.
- `esp32s3cam/` is **not** a git repository, so the plan has no commit steps. Run the test suite at the end of each task instead.
- Test command (from `esp32s3cam/`): `../.venv/bin/python -m pytest tests -q`

## Review Focus

1. **The user's real parts differ from the nominal numbers** (servo, horn, HC-SR04 and laser are estimates). Parts must still rebuild when a constant changes. Task 7 includes a test that perturbs key constants and rebuilds.
2. **The wire loop snags at the pan extremes.** The neck-cap wire window must stay open over the full ±90° sweep, for a bundle of 13 Ø1.4 mm wires. Task 4 includes a test.
3. **USB-C reflashing.** A cable plug overmold (12.5 × 7.5 mm, 25 mm long) plugged in from below must clear the yoke and neck at tilt +90°. Task 7 includes a test.
4. **SD card removal.** At tilt 0°, the card's protrusion plus a 6 mm fingertip box beyond it must clear the pin arm. Task 7 includes a test.
5. **Laser not parallel to the camera.** The laser clamp's bore axis must be parallel to the camera axis (+Y in the head frame) and must not intersect the eye openings. Task 6 includes a test.

---

## File structure (all under `esp32s3cam/`)

| File | Responsibility |
|---|---|
| `params.py` | Every dimension, clearance, range and switch. `Bearing` dataclass. No geometry. |
| `components.py` | Reference models and keep-out volumes of bought parts (board, HC-SR04, laser, MG90S, horn, bearing). |
| `base.py` | Base plate + neck lower body (pan servo pocket, cable path). |
| `pan.py` | Neck cap (pan bearing seat, wire window), pan coupler (horn pocket), printed bushing. |
| `yoke.py` | Yoke: pan stub shaft, tilt-servo arm (−X), pin arm with tilt bearing (+X). |
| `head.py` | Head front shell (face, eyes, laser clamp, board standoffs, openings) and rear cover. |
| `gimbal_head.py` | Entry point: `place()`, checks, STL export, viewer. Module docstring = user guide. |
| `make_3mf.py` | Bambu Studio project from the STLs (adapted from `tv/make_3mf.py`). |
| `conftest.py` | Empty. Puts `esp32s3cam/` on `sys.path` for pytest. |
| `tests/test_*.py` | One test file per module above. |

---

### Task 1: Parameters and test scaffold

**Files:**
- Create: `esp32s3cam/params.py`, `esp32s3cam/conftest.py`, `esp32s3cam/tests/test_params.py`

**Interfaces:**
- Produces: `params` module with the constants below, plus `@dataclass(frozen=True) class Bearing: bore: float; od: float; width: float`.

Constants (names fixed; values from DESIGN.md §4.1, §5 and this list). All positions on the board are **as seen from the front, measured from the board's top-left corner, with USB-C down**:
- Board: `BOARD_W = 30.4`, `BOARD_H = 38.4`, `PCB_T = 1.6`, `BOARD_HOLE_INSET = 3.2`, `BOARD_HOLE_D = 3.0`.
- Camera: `LENS_X = BOARD_W / 2`, `LENS_Y = 10.0`, `CAM_MODULE = 8.5`, `CAM_H = 6.0` (lens top above the PCB front), `LENS_WINDOW_D = 7.5`.
- Flash LEDs: `LED_XS = (9.5, 23.2)`, `LED_Y = 7.5`, `LED_WINDOW = 3.0`.
- SD: `SD_X0 = 2.7`, `SD_Y0 = 5.8`, `SD_SHELL_W = 4.8`, `SD_SHELL_L = 10.6`, `SD_SHELL_H = 2.0`, `SD_CARD_W = 11.0`, `SD_CARD_T = 1.0`, `SD_CARD_OUT = 4.0` (how far the card sticks out past the board's left edge, as seen from the front, i.e. +X). `SD_FINGER = 6.0`.
- USB-C: `USB_W = 9.0`, `USB_H = 3.3`, `USB_OVERHANG = 0.8`. Plug: `USB_PLUG_W = 12.5`, `USB_PLUG_T = 7.5`, `USB_PLUG_L = 25.0`.
- Buttons: `BTN_XS = (8.1, 22.9)`, `BTN_Y = 32.9`, `PINHOLE_D = 2.0`.
- Headers: `HDR_X_INSET = 1.3`, `HDR_PITCH = 2.54`, `HDR_COUNT = 8`, `HDR_Y0 = 7.9`, `HDR_BACK = 8.5`, `DUPONT_L = 14.0`, `DUPONT_W = 2.6`, `BAY_DEPTH = 30.0`.
- HC-SR04: `SR_W = 45.0`, `SR_H = 20.0`, `SR_PCB_T = 1.6`, `SR_TX_D = 16.2`, `SR_TX_H = 12.0`, `SR_TX_DX = 26.0` (center spacing), `SR_PIN_LEN = 6.0` (pins leave the bottom edge, pointing −Z in the PCB plane), `SR_BACK_H = 3.0`.
- Laser: `LASER_D = 12.0`, `LASER_L = 35.0`.
- MG90S: `SERVO_L = 22.8`, `SERVO_W = 12.2`, `SERVO_H = 22.7`, `SERVO_TAB_L = 32.3`, `SERVO_TAB_T = 2.5`, `SERVO_TAB_Z = 15.9` (tab underside above the body bottom), `SERVO_TAB_HOLE_PITCH = 27.8`, `SERVO_SHAFT_OFFSET = 5.9` (shaft center from the near body end), `SERVO_SHAFT_H = 4.0` (spline top above the case top).
- Horn (MG90S double arm, measure the real one): `HORN_HUB_D = 7.2`, `HORN_HUB_H = 4.4`, `HORN_ARM_L = 16.0` (hub center to tip), `HORN_ARM_W_HUB = 6.0`, `HORN_ARM_W_TIP = 4.0`, `HORN_ARM_T = 1.8`.
- Bearings: `PAN_BEARING = Bearing(8, 22, 7)`, `TILT_BEARING = Bearing(3, 10, 4)`, `USE_PAN_BEARING = True`, `USE_TILT_BEARING = True`, `TILT_AXLE_D = 3.0`.
- Base: `BASE_L = 41.8`, `BASE_W = 30.8`, `BASE_CORNER_R = 3.0`, `BASE_HOLE_D = 2.2`, `BASE_HOLE_DX = 22.0`, `BASE_HOLE_DY = 33.0`, `BASE_CBORE_D = 4.4`, `BASE_CBORE_DEPTH = 2.2`, `BASE_BOSS_H = 4.4`, `BASE_PLATE_T = 2.4`, `BASE_LONG_AXIS = "Y"` (`"X"` or `"Y"`, which world axis the 41.8 side runs along).
- Motion and fits: `PAN_RANGE = (-90, 90)`, `TILT_RANGE = (-45, 90)`, `FIT = 0.25` (sliding clearance), `PRESS = 0.05` (bearing seat diameter = od + PRESS), `MOVE_CLR = 0.5`, `WALL = 2.0`, `M2_CLEAR = 2.2`, `M2_PILOT = 1.7`.
- Wires: `WIRE_COUNT = 13`, `WIRE_D = 1.4`.

- [ ] **Step 1: Install pytest into the project venv**

Run: `/Users/ricardo/Projects/3D/build123d/.venv/bin/python -m pip install pytest`
Expected: `Successfully installed pytest-…` (or "already satisfied")

- [ ] **Step 2: Write the failing tests** in `tests/test_params.py`

```python
import params as p

def test_base_pattern_matches_reference():
    assert (p.BASE_L, p.BASE_W) == (41.8, 30.8)
    assert (p.BASE_HOLE_DX, p.BASE_HOLE_DY, p.BASE_HOLE_D) == (22.0, 33.0, 2.2)
    assert (p.BASE_CBORE_D, p.BASE_CBORE_DEPTH) == (4.4, 2.2)

def test_bearing_defaults():
    assert p.PAN_BEARING == p.Bearing(8, 22, 7)
    assert p.TILT_BEARING == p.Bearing(3, 10, 4)

def test_ranges():
    assert p.PAN_RANGE == (-90, 90) and p.TILT_RANGE == (-45, 90)

def test_board_features_on_board():
    for x in (p.LENS_X, *p.LED_XS, p.SD_X0, *p.BTN_XS):
        assert 0 <= x <= p.BOARD_W
    assert p.LENS_X == p.BOARD_W / 2
```

- [ ] **Step 3: Run it to verify it fails**

Run: `cd esp32s3cam && ../.venv/bin/python -m pytest tests/test_params.py -q`
Expected: FAIL, `ModuleNotFoundError: No module named 'params'`

- [ ] **Step 4: Create `conftest.py` (empty, with a one-line comment) and `params.py` with the constants above**

- [ ] **Step 5: Run it to verify it passes**

Run: `cd esp32s3cam && ../.venv/bin/python -m pytest tests -q`
Expected: 4 passed

---

### Task 2: Reference models of bought parts

**Files:**
- Create: `esp32s3cam/components.py`, `esp32s3cam/tests/test_components.py`

**Interfaces:**
- Consumes: `params`.
- Produces (each returns a `Part` in its own local frame):
  - `esp32_board() -> Part`. Origin at the center of the PCB's front face. Camera looks +Y, USB-C toward −Z, SD side toward +X. Includes the PCB, camera module, SD shell, LEDs, USB-C, buttons and header pins sticking out −Y.
  - `esp32_keepout() -> Part`. The board plus the Dupont bay: a box `BAY_DEPTH` deep behind the PCB covering the full board outline.
  - `sd_access() -> Part`. The SD card protrusion `SD_CARD_OUT` past the +X edge plus a fingertip box `SD_FINGER` beyond it, at the card's height. Same frame as the board.
  - `usb_plug() -> Part`. The cable plug overmold (`USB_PLUG_W × USB_PLUG_T × USB_PLUG_L`) extending −Z from the USB-C. Same frame as the board.
  - `hcsr04() -> Part` / `hcsr04_keepout() -> Part`. Origin at the PCB front-face center. Transducers at x = ±`SR_TX_DX`/2 pointing +Y, pins toward −Z. The keepout adds a Dupont box `DUPONT_L` + 8 long below the pins and `SR_BACK_H` behind the PCB.
  - `laser() -> Part`. Origin at the center of the rear end, axis +Y.
  - `mg90s() -> Part`. Origin on the shaft axis in the plane of the case top, shaft along +Z, long side along X, body center at x = −(`SERVO_L`/2 − `SERVO_SHAFT_OFFSET`). Includes the tabs with holes.
  - `mg90s_horn() -> Part`. Origin on the hub axis at the hub face that sits on the servo, extending +Z, arms along ±X.
  - `bearing(b: Bearing) -> Part`. Ring centered at the origin, axis Z, width centered on Z = 0.

- [ ] **Step 1: Write the failing tests** in `tests/test_components.py`

```python
import pytest
from build123d import Vector
import params as p
import components as c

def size(part):
    bb = part.bounding_box(); return (bb.size.X, bb.size.Y, bb.size.Z)

def test_board_pcb_outline():
    sx, _, sz = size(c.esp32_board())
    assert sx == pytest.approx(p.BOARD_W, abs=0.01)
    assert sz == pytest.approx(p.BOARD_H + p.USB_OVERHANG, abs=0.01)

def test_board_lens_position():
    # lens on +Y side, centered in X, LENS_Y below the top edge
    top = p.BOARD_H / 2
    probe = Vector(p.LENS_X - p.BOARD_W / 2, p.PCB_T / 2 + 1, top - p.LENS_Y)
    assert c.esp32_board().is_inside(probe)

def test_keepouts():
    assert c.esp32_keepout().bounding_box().min.Y == pytest.approx(-p.BAY_DEPTH, abs=0.01)
    sd = c.sd_access().bounding_box()
    assert sd.min.X == pytest.approx(p.BOARD_W / 2, abs=0.01)
    assert sd.max.X == pytest.approx(p.BOARD_W / 2 + p.SD_CARD_OUT + p.SD_FINGER, abs=0.01)
    usb = c.usb_plug().bounding_box()
    assert usb.max.Z <= -p.BOARD_H / 2 + 0.01
    assert usb.size.Z == pytest.approx(p.USB_PLUG_L, abs=0.01)

def test_hcsr04_and_laser_sizes():
    sx, sy, sz = size(c.hcsr04())
    assert sx == pytest.approx(p.SR_W, abs=0.01)
    assert sy >= p.SR_TX_H
    lx, ly, lz = size(c.laser())
    assert (lx, ly, lz) == pytest.approx((p.LASER_D, p.LASER_L, p.LASER_D), abs=0.01)

def test_servo_shaft_at_origin():
    s = c.mg90s()
    assert s.is_inside(Vector(0, 0, p.SERVO_SHAFT_H / 2))
    assert s.bounding_box().size.X == pytest.approx(p.SERVO_TAB_L, abs=0.01)

def test_bearing_envelope():
    b = c.bearing(p.PAN_BEARING)
    assert size(b) == pytest.approx((22, 22, 7), abs=0.01)
    assert not b.is_inside(Vector(0, 0, 0))
```

- [ ] **Step 2: Run them to verify they fail**

Run: `cd esp32s3cam && ../.venv/bin/python -m pytest tests/test_components.py -q`
Expected: FAIL, `No module named 'components'`

- [ ] **Step 3: Implement the functions in `components.py`.** Use simple boxes and cylinders. These are references and keep-outs, not detailed models.

- [ ] **Step 4: Run the suite to verify it passes**

Run: `cd esp32s3cam && ../.venv/bin/python -m pytest tests -q`
Expected: all passed

---

### Task 3: Base plate and neck body

**Files:**
- Create: `esp32s3cam/base.py`, `esp32s3cam/tests/test_base.py`

**Interfaces:**
- Consumes: `params`, `components.mg90s`.
- Produces:
  - `make_base(long_axis: str = params.BASE_LONG_AXIS) -> Part`, in the world frame.
  - `PAN_SERVO_LOC: Location`. The `mg90s()` frame in the world, with the shaft on the Z axis pointing +Z.
  - `NECK_TOP_Z: float`. The plane where the neck cap (Task 4) sits.
  - `CABLE_HOLE: tuple[float, float]`. The pass-through size (X, Y) through the plate.

The neck is a rounded column, outer size chosen so the servo with tabs fits with `WALL`. **Spec conflict, resolved here:** with the shaft on the plate center, the MG90S tabs reach about 21.7 mm from the axis, which is past the plate's 20.9 mm half-length. The neck may therefore overhang the plate along the long axis, but only above `BASE_BOSS_H`, and by no more than 3 mm. The plate itself stays exactly 41.8 × 30.8. The neck must leave vertical screwdriver access above all 4 counterbores (neck half-width across the short axis ≤ `BASE_HOLE_DX/2 - BASE_CBORE_D/2 - 0.5`). The servo drops in from the top and hangs on its tabs, with M2 pilot holes (`M2_PILOT`) under the tab holes. A cable channel runs from `NECK_TOP_Z` down beside the servo to the plate pass-through. The base plate and neck are one printed part.

- [ ] **Step 1: Write the failing tests** in `tests/test_base.py`

```python
import pytest
from build123d import Vector
import params as p
import components as c
import base

@pytest.fixture(scope="module")
def b(): return base.make_base()

def test_valid_single_solid(b):
    assert b.is_valid and len(b.solids()) == 1

def test_footprint(b):
    bb = b.bounding_box()
    assert bb.min.Z == pytest.approx(0, abs=1e-6)
    assert bb.size.X == pytest.approx(p.BASE_W, abs=0.01)
    assert p.BASE_L - 0.01 <= bb.size.Y <= p.BASE_L + 6.0

def test_plate_outline_at_z1(b):
    # long side along Y by default
    assert b.is_inside(Vector(p.BASE_W / 2 - 0.5, 0, 1))
    assert not b.is_inside(Vector(p.BASE_W / 2 + 0.5, 0, 1))
    assert b.is_inside(Vector(0, p.BASE_L / 2 - 0.5, 1))
    assert not b.is_inside(Vector(0, p.BASE_L / 2 + 0.5, 1))

@pytest.mark.parametrize("sx", [-1, 1])
@pytest.mark.parametrize("sy", [-1, 1])
def test_screw_holes_and_counterbores(b, sx, sy):
    x, y = sx * p.BASE_HOLE_DX / 2, sy * p.BASE_HOLE_DY / 2
    assert not b.is_inside(Vector(x + 1.0, y, 1.0))        # Ø2.2 through hole
    assert b.is_inside(Vector(x + 1.4, y, 1.0))            # plate around it
    assert not b.is_inside(Vector(x + 2.0, y, p.BASE_BOSS_H - 1.0))  # Ø4.4 counterbore
    for z in (p.BASE_BOSS_H + 2, base.NECK_TOP_Z):                  # screwdriver access
        assert not b.is_inside(Vector(x, y, z))

def test_long_axis_switch():
    bb = base.make_base("X").bounding_box()
    assert bb.size.Y == pytest.approx(p.BASE_W, abs=0.01)
    assert bb.size.X >= p.BASE_L - 0.01

def test_pan_servo_fits(b):
    servo = c.mg90s().moved(base.PAN_SERVO_LOC)
    assert (servo & b).volume < 0.01

def test_cable_hole_fits_bundle():
    w, d = base.CABLE_HOLE
    assert w * d >= p.WIRE_COUNT * p.WIRE_D ** 2 * 1.5
```

- [ ] **Step 2: Run them to verify they fail**

Run: `cd esp32s3cam && ../.venv/bin/python -m pytest tests/test_base.py -q`
Expected: FAIL, `No module named 'base'`

- [ ] **Step 3: Implement `make_base`, `PAN_SERVO_LOC`, `NECK_TOP_Z`, `CABLE_HOLE` in `base.py`**

- [ ] **Step 4: Run the suite to verify it passes**

Run: `cd esp32s3cam && ../.venv/bin/python -m pytest tests -q`
Expected: all passed

---

### Task 4: Pan bearing parts (neck cap, coupler, bushing)

**Files:**
- Create: `esp32s3cam/pan.py`, `esp32s3cam/tests/test_pan.py`

**Interfaces:**
- Consumes: `params`, `components.bearing`, `components.mg90s_horn`, `base.NECK_TOP_Z`, `base.PAN_SERVO_LOC`.
- Produces:
  - `make_neck_cap(b: Bearing = params.PAN_BEARING) -> Part`. Screws onto the neck top (M2). Holds the bearing in a seat of Ø `b.od + PRESS`, depth `b.width`, coaxial with the pan axis. Has an **arc-shaped wire window** beside the seat, spanning at least the pan range plus the bundle width.
  - `make_pan_coupler(b: Bearing = params.PAN_BEARING) -> Part`. A disc below the bearing with a horn pocket (`mg90s_horn` + `FIT`) facing down, and an M2 screw hole up into the yoke stub. Its top face clamps the bearing's inner ring.
  - `make_bushing(b: Bearing) -> Part`. Printed stand-in: OD `b.od`, bore `b.bore + 2*FIT`, width `b.width`.
  - `PAN_BEARING_LOC: Location`. Bearing center in the world frame.
  - `STUB_D(b: Bearing) -> float`. Returns `b.bore - 0.1`, the yoke stub diameter (used by Task 5). Stub bore for the horn-screw screwdriver: `max(b.bore - 3.5, 3.0)`.

Assembly the parts must allow (put this in the `pan.py` docstring): bearing pressed into the cap → yoke stub through the bearing from above → coupler screwed to the stub from below (clamping the inner ring) → horn screwed into the coupler pocket → cap and yoke lowered onto the neck so the horn engages the servo spline → cap screwed to the neck → horn center screw driven through the hollow stub.

- [ ] **Step 1: Write the failing tests** in `tests/test_pan.py`

```python
import math, pytest
from build123d import Vector
import params as p
import components as c
import base, pan

def test_cap_holds_bearing():
    cap = pan.make_neck_cap()
    brg = c.bearing(p.PAN_BEARING).moved(pan.PAN_BEARING_LOC)
    assert cap.is_valid and (cap & brg).volume < 0.01
    # seat wall surrounds it
    r = p.PAN_BEARING.od / 2 + 0.5
    z = pan.PAN_BEARING_LOC.position.Z
    assert cap.is_inside(Vector(r + 0.5, 0, z))

def test_wire_window_open_over_pan_range():
    cap = pan.make_neck_cap()
    z = base.NECK_TOP_Z + 1.0
    # some radius exists where every 15° step from -90..+90 (plus bundle) is open
    radii = [p.PAN_BEARING.od / 2 + k for k in (2, 3, 4, 5)]
    def open_at(rad):
        return all(not cap.is_inside(Vector(rad * math.sin(math.radians(a)),
                                            -rad * math.cos(math.radians(a)), z))
                   for a in range(-90, 91, 15))
    assert any(open_at(r) for r in radii)

def test_coupler_takes_horn():
    cp = pan.make_pan_coupler()
    assert cp.is_valid

@pytest.mark.parametrize("b", [p.Bearing(8, 22, 7), p.Bearing(25, 37, 7)])
def test_other_bearing_sizes_build(b):
    assert pan.make_neck_cap(b).is_valid and pan.make_pan_coupler(b).is_valid

def test_bushing_envelope():
    bb = pan.make_bushing(p.PAN_BEARING).bounding_box()
    assert (bb.size.X, bb.size.Z) == pytest.approx((22, 7), abs=0.01)
```

The window test assumes the wire window is behind the pan axis (−Y). If you put it elsewhere, rotate the probe angles to match and say so in a comment.

- [ ] **Step 2: Run them to verify they fail**

Run: `cd esp32s3cam && ../.venv/bin/python -m pytest tests/test_pan.py -q`
Expected: FAIL, `No module named 'pan'`

- [ ] **Step 3: Implement `pan.py`**

- [ ] **Step 4: Run the suite to verify it passes**

Run: `cd esp32s3cam && ../.venv/bin/python -m pytest tests -q`
Expected: all passed

---

### Task 5: Yoke

**Files:**
- Create: `esp32s3cam/yoke.py`, `esp32s3cam/tests/test_yoke.py`

**Interfaces:**
- Consumes: `params`, `components.mg90s`, `components.bearing`, `pan.STUB_D`, `pan.PAN_BEARING_LOC`.
- Produces:
  - `make_yoke(pan_b: Bearing = params.PAN_BEARING, tilt_b: Bearing = params.TILT_BEARING) -> Part`. In the yoke frame, which equals the world frame at pan 0. Includes the hollow stub of Ø `STUB_D(pan_b)` going down through the bearing, a shoulder resting on the inner ring, the crossbar, the **−X arm** housing the tilt servo (shaft on the tilt axis pointing +X), and the slim **+X arm** holding the tilt bearing (seat Ø `tilt_b.od + PRESS`).
  - `TILT_AXIS_Z: float`. Height of the tilt axis (along X, through Y = 0).
  - `TILT_SERVO_LOC: Location`. The `mg90s()` frame in the yoke frame.
  - `TILT_BEARING_LOC: Location`. Bearing center, axis along X.
  - `PIN_ARM_TOP_Z: float`. Highest point of the +X arm.
  - `ARM_INNER_X: float`. Half the gap between the arms (the head's maximum half-width at the pivot is `ARM_INNER_X - MOVE_CLR`).

- [ ] **Step 1: Write the failing tests** in `tests/test_yoke.py`

```python
import pytest
import params as p
import components as c
import yoke

@pytest.fixture(scope="module")
def y(): return yoke.make_yoke()

def test_valid(y):
    assert y.is_valid and len(y.solids()) == 1

def test_tilt_servo_in_minus_x_arm(y):
    s = c.mg90s().moved(yoke.TILT_SERVO_LOC)
    assert (s & y).volume < 0.01
    assert s.bounding_box().max.X < 0

def test_tilt_bearing_in_plus_x_arm(y):
    brg = c.bearing(p.TILT_BEARING).moved(yoke.TILT_BEARING_LOC)
    assert (brg & y).volume < 0.01
    assert yoke.TILT_BEARING_LOC.position.X > 0
    assert yoke.TILT_BEARING_LOC.position.Z == pytest.approx(yoke.TILT_AXIS_Z)

def test_pin_arm_stops_near_pivot():
    # leaves the SD card (above the pivot on the +X side) uncovered
    assert yoke.PIN_ARM_TOP_Z <= yoke.TILT_AXIS_Z + p.TILT_BEARING.od / 2 + p.WALL + 0.01

def test_other_bearings_build():
    assert yoke.make_yoke(p.Bearing(25, 37, 7), p.Bearing(5, 16, 5)).is_valid
```

- [ ] **Step 2: Run them to verify they fail**

Run: `cd esp32s3cam && ../.venv/bin/python -m pytest tests/test_yoke.py -q`
Expected: FAIL, `No module named 'yoke'`

- [ ] **Step 3: Implement `yoke.py`**

Choose `TILT_AXIS_Z` so the head (Task 6) swept through −45…+90° clears the neck cap. Task 7's motion test is the arbiter; expect to revisit this value there.

- [ ] **Step 4: Run the suite to verify it passes**

Run: `cd esp32s3cam && ../.venv/bin/python -m pytest tests -q`
Expected: all passed

---

### Task 6: Head (front shell + rear cover)

**Files:**
- Create: `esp32s3cam/head.py`, `esp32s3cam/tests/test_head.py`

**Interfaces:**
- Consumes: `params`, `components.*`, `yoke.ARM_INNER_X`, `components.mg90s_horn`.
- Produces (head frame: origin on the tilt axis midway between the arms, +Y forward at tilt 0, +Z up):
  - `make_head_front() -> Part`. Face with two eye openings (Ø `SR_TX_D + 2*FIT`) and raised brow rings, lens window, 2 LED windows, board standoffs on the 4 board holes, the HC-SR04 shelf with a slot for its pins, the laser split-clamp on top (bore `LASER_D + FIT`, M2 pinch screw, axis +Y), the USB-C opening in the bottom (fits `USB_PLUG_W × USB_PLUG_T`), BOOT/RESET pinholes (`PINHOLE_D`), the SD slot in the +X side wall, the horn pocket in the −X side boss, and an M3 pilot (Ø 2.5) for the tilt axle in the +X boss.
  - `make_head_rear() -> Part`. Rear cover closing the Dupont bay, attached with M2 screws, with a wire exit near the tilt axis on the underside.
  - `BOARD_LOC`, `SR04_LOC`, `LASER_LOC: Location`. Component frames in the head frame.

Shape: wide at the eyes (set by HC-SR04), tapering to the narrower board body. Rounded edges. The overall half-width at the pivot must be ≤ `ARM_INNER_X - MOVE_CLR`.

- [ ] **Step 1: Write the failing tests** in `tests/test_head.py`

```python
import pytest
from build123d import Vector, Location
import params as p
import components as c
import head, yoke

def pt(loc, x, y, z):
    """Point given in a component frame, expressed in the head frame"""
    return (loc * Location((x, y, z))).position

@pytest.fixture(scope="module")
def front(): return head.make_head_front()
@pytest.fixture(scope="module")
def rear(): return head.make_head_rear()

def test_valid(front, rear):
    assert front.is_valid and rear.is_valid

@pytest.mark.parametrize("keepout,loc", [
    ("esp32_keepout", "BOARD_LOC"), ("sd_access", "BOARD_LOC"), ("usb_plug", "BOARD_LOC"),
    ("hcsr04_keepout", "SR04_LOC"), ("laser", "LASER_LOC")])
def test_components_clear_shells(front, rear, keepout, loc):
    k = getattr(c, keepout)().moved(getattr(head, loc))
    assert (k & front).volume < 0.01 and (k & rear).volume < 0.01

def test_front_and_rear_do_not_overlap(front, rear):
    assert (front & rear).volume < 0.5   # tongue/groove contact only

def test_lens_window_open(front):
    x, z = p.LENS_X - p.BOARD_W / 2, p.BOARD_H / 2 - p.LENS_Y
    for dy in (p.CAM_H + 0.5, p.CAM_H + 3):
        assert not front.is_inside(pt(head.BOARD_LOC, x, p.PCB_T / 2 + dy, z))

def test_eyes_open(front):
    for sx in (-1, 1):
        tip = pt(head.SR04_LOC, sx * p.SR_TX_DX / 2, p.SR_PCB_T / 2 + p.SR_TX_H + 0.5, 0)
        assert not front.is_inside(tip)

def test_button_pinholes_open(front):
    for bx in p.BTN_XS:
        for dy in (3.0, 6.0):
            assert not front.is_inside(pt(head.BOARD_LOC, bx - p.BOARD_W / 2, dy, p.BOARD_H / 2 - p.BTN_Y))

def test_laser_parallel_to_camera():
    axis = pt(head.LASER_LOC, 0, 1, 0) - pt(head.LASER_LOC, 0, 0, 0)
    assert axis.normalized().Y == pytest.approx(1, abs=1e-6)

def test_fits_between_arms(front, rear):
    for part in (front, rear):
        bb = part.bounding_box()
        assert max(abs(bb.min.X), abs(bb.max.X)) <= yoke.ARM_INNER_X - p.MOVE_CLR + 1e-6
```

- [ ] **Step 2: Run them to verify they fail**

Run: `cd esp32s3cam && ../.venv/bin/python -m pytest tests/test_head.py -q`
Expected: FAIL, `No module named 'head'`

- [ ] **Step 3: Implement `head.py`**

- [ ] **Step 4: Run the suite to verify it passes**

Run: `cd esp32s3cam && ../.venv/bin/python -m pytest tests -q`
Expected: all passed

---

### Task 7: Assembly, motion and access checks

**Files:**
- Create: `esp32s3cam/gimbal_head.py` (the `place()` part and checks only), `esp32s3cam/tests/test_motion.py`

**Interfaces:**
- Consumes: everything above.
- Produces:
  - `place(pan_deg: float, tilt_deg: float) -> dict[str, Part]`. Keys: `"base", "neck_cap", "pan_coupler", "yoke", "head_front", "head_rear", "board", "hcsr04", "laser", "pan_servo", "tilt_servo", "pan_bearing", "tilt_bearing"`. Positive tilt = looking up (the camera axis rotates from +Y toward +Z). Positive pan = turning toward +X. When a bearing is switched off, its key holds the bushing.
  - `STATIC = {"base", "neck_cap", "pan_servo", "pan_bearing"}`, `PANNING = {"yoke", "pan_coupler", "tilt_servo", "tilt_bearing"}`, `TILTING = {"head_front", "head_rear", "board", "hcsr04", "laser"}`.
  - `head_to_world(pan_deg: float, tilt_deg: float) -> Location`. The head frame in the world.
  - `joint_zone(pan_deg: float) -> Part`. Where head and yoke touch on purpose: a cylinder on the tilt axis at each arm's inner face, radius `HORN_ARM_L + 2` on −X and `TILT_BEARING.od/2 + 2` on +X, spanning `ARM_INNER_X - 4` outward. Distance checks ignore it; no-overlap checks don't.
  - `run_checks() -> None`. Asserts everything below with readable messages. Called by the script's `__main__`.

- [ ] **Step 1: Write the failing tests** in `tests/test_motion.py`

```python
import pytest
from build123d import Box, Location, Vector
import params as p
import gimbal_head as g

def group(parts, names):
    out = None
    for n in names:
        out = parts[n] if out is None else out + parts[n]
    return out

TILTS = list(range(p.TILT_RANGE[0], p.TILT_RANGE[1] + 1, 15))

@pytest.mark.parametrize("tilt", TILTS)
def test_tilting_never_overlaps(tilt):
    parts = g.place(0, tilt)
    moving = group(parts, g.TILTING)
    fixed = group(parts, g.PANNING | g.STATIC)
    assert (moving & fixed).volume < 0.01, f"tilt {tilt}°"

@pytest.mark.parametrize("tilt", TILTS)
def test_tilting_keeps_clearance(tilt):
    parts = g.place(0, tilt)
    moving = group(parts, g.TILTING) - g.joint_zone(0)
    fixed = group(parts, (g.PANNING | g.STATIC) - {"tilt_servo", "tilt_bearing"}) - g.joint_zone(0)
    assert moving.distance_to(fixed) >= p.MOVE_CLR - 1e-3, f"tilt {tilt}°"

@pytest.mark.parametrize("pan", [p.PAN_RANGE[0], 0, p.PAN_RANGE[1]])
@pytest.mark.parametrize("tilt", [p.TILT_RANGE[0], p.TILT_RANGE[1]])
def test_panning_clears_base(pan, tilt):
    parts = g.place(pan, tilt)
    moving = group(parts, g.PANNING | g.TILTING) - parts["pan_coupler"]
    fixed = parts["base"]
    assert moving.distance_to(fixed) >= p.MOVE_CLR - 1e-3

def test_usb_plug_reachable_at_tilt_up():
    import components as c, head
    parts = g.place(0, p.TILT_RANGE[1])
    plug = c.usb_plug().moved(g.head_to_world(0, p.TILT_RANGE[1]) * head.BOARD_LOC)
    others = group(parts, g.PANNING | g.STATIC)
    assert (plug & others).volume < 0.01

def test_sd_card_reachable_at_rest():
    import components as c, head
    parts = g.place(0, 0)
    ko = c.sd_access().moved(g.head_to_world(0, 0) * head.BOARD_LOC)
    assert (ko & parts["yoke"]).volume < 0.01

@pytest.mark.parametrize("name,delta", [("SERVO_W", 0.4), ("HORN_HUB_D", 0.4),
                                        ("SR_TX_D", 0.5), ("LASER_D", 0.3)])
def test_rebuilds_with_perturbed_params(name, delta):
    import importlib, params, components, base, pan, yoke, head
    import gimbal_head
    mods = (params, components, base, pan, yoke, head, gimbal_head)
    try:
        importlib.reload(params)
        setattr(params, name, getattr(params, name) + delta)
        for m in mods[1:]:
            importlib.reload(m)
        parts = gimbal_head.place(0, 0)
        assert all(part.is_valid for part in parts.values())
    finally:
        for m in mods:
            importlib.reload(m)
```

Modules use `import params as p` and read `p.X`, never `from params import X`. That way the reload in the perturbation test, and the call-time switches in Task 8, take effect. Other test modules must re-import (`import gimbal_head as g` inside tests, or module-level imports that are reloaded) if they run after the perturbation test. Keep `test_motion.py` last alphabetically or run it in its own process if this bites.

- [ ] **Step 2: Run them to verify they fail**

Run: `cd esp32s3cam && ../.venv/bin/python -m pytest tests/test_motion.py -q`
Expected: FAIL, `No module named 'gimbal_head'`

- [ ] **Step 3: Implement `place`, `head_to_world`, the group sets and `run_checks` in `gimbal_head.py`.** Then tune `yoke.TILT_AXIS_Z`, the head's taper and the neck-cap height until the motion tests pass. Never relax `MOVE_CLR`.

- [ ] **Step 4: Run the suite to verify it passes**

Run: `cd esp32s3cam && ../.venv/bin/python -m pytest tests -q`
Expected: all passed

---

### Task 8: Export, viewer and user docstring

**Files:**
- Modify: `esp32s3cam/gimbal_head.py`
- Create: `esp32s3cam/tests/test_export.py`

**Interfaces:**
- Produces:
  - `printed_parts() -> dict[str, Callable[[], Part]]`. Read at call time, so the `USE_*_BEARING` switches apply. Keys `base, neck_cap, pan_coupler, yoke, head_front, head_rear` (+ `pan_bushing`, `tilt_bushing`). STL names: `gimbal_base.stl`, `gimbal_neck_cap.stl`, `gimbal_pan_coupler.stl`, `gimbal_yoke.stl`, `gimbal_head_front.stl`, `gimbal_head_rear.stl`, plus `gimbal_pan_bushing.stl` / `gimbal_tilt_bushing.stl` only when the matching `USE_*_BEARING` is False.
  - `export_all(out_dir: Path) -> list[Path]`. Writes each part rotated to its print orientation, resting at Z = 0.
  - The `__main__` block runs `run_checks()`, then `export_all(Path(__file__).parent)`, then `show(...)` of `place(0, 0)` with names and colors (head semi-transparent). If the viewer is unavailable it prints a note, like `tv/ir_remote_case.py`.
  - The module docstring covers: frames, parts list, the bought-parts/hardware list (2 × MG90S, 608 + 623 bearings or bushings, M3 axle screw, M2 screws with counts), assembly order (from the `pan.py` docstring plus the head and tilt steps), viewing instructions, print orientation and support per part, and the electronics notes from DESIGN.md §7.

- [ ] **Step 1: Write the failing tests** in `tests/test_export.py`

```python
import pytest
import params as p
import gimbal_head as g

def test_export_writes_printed_parts(tmp_path):
    files = g.export_all(tmp_path)
    names = sorted(f.name for f in files)
    assert names == sorted(["gimbal_base.stl", "gimbal_neck_cap.stl", "gimbal_pan_coupler.stl",
                            "gimbal_yoke.stl", "gimbal_head_front.stl", "gimbal_head_rear.stl"])
    assert all(f.stat().st_size > 1000 for f in files)

def test_bushings_exported_when_bearings_off(tmp_path, monkeypatch):
    monkeypatch.setattr(p, "USE_PAN_BEARING", False)
    monkeypatch.setattr(p, "USE_TILT_BEARING", False)
    names = {f.name for f in g.export_all(tmp_path)}
    assert {"gimbal_pan_bushing.stl", "gimbal_tilt_bushing.stl"} <= names

@pytest.mark.parametrize("name", ["base", "neck_cap", "pan_coupler", "yoke", "head_front", "head_rear"])
def test_print_orientation_rests_on_bed(name):
    part = g.print_oriented(name)
    bb = part.bounding_box()
    assert bb.min.Z == pytest.approx(0, abs=1e-6)
    bed = [f for f in part.faces() if abs(f.center().Z) < 1e-4 and abs(f.normal_at().Z) > 0.99]
    assert sum(f.area for f in bed) > 50  # a real first layer, not a point
```

This adds `print_oriented(name: str) -> Part` to the interface. `export_all` uses it.

- [ ] **Step 2: Run them to verify they fail**

Run: `cd esp32s3cam && ../.venv/bin/python -m pytest tests/test_export.py -q`
Expected: FAIL, `AttributeError: module 'gimbal_head' has no attribute 'export_all'`

- [ ] **Step 3: Implement `printed_parts`, `print_oriented`, `export_all`, the `__main__` block and the docstring**

- [ ] **Step 4: Run the suite and the script**

Run: `cd esp32s3cam && ../.venv/bin/python -m pytest tests -q && ../.venv/bin/python gimbal_head.py`
Expected: all tests pass. The script prints its checks, writes the 6 STL files next to it, and either shows the model or prints "viewer unavailable".

---

### Task 9: Bambu Studio project

**Files:**
- Create: `esp32s3cam/make_3mf.py` (adapted from `tv/make_3mf.py`; same printer/process/filament: A1 0.4, 0.16 mm High Quality, Bambu PLA Matte)

**Interfaces:**
- Consumes: the STL files from Task 8. Reads `gimbal_head.printed_parts()` and the per-part support flag `gimbal_head.NEEDS_SUPPORT: dict[str, bool]` (add it in this task, keys covering all 8 possible parts) to build the `models` dict.
- Produces: `esp32s3cam/gimbal_head.3mf`.

- [ ] **Step 1: Add `NEEDS_SUPPORT` to `gimbal_head.py` and a test** in `tests/test_export.py`:

```python
def test_support_flags_cover_printed_parts():
    assert set(g.printed_parts()) <= set(g.NEEDS_SUPPORT)
    assert {"pan_bushing", "tilt_bushing"} <= set(g.NEEDS_SUPPORT)
```

- [ ] **Step 2: Write `make_3mf.py`** by copying `tv/make_3mf.py`'s structure. Change only `models`, which is built from `printed_parts()` + `NEEDS_SUPPORT`, and `output`.

- [ ] **Step 3: Run it**

Run: `cd esp32s3cam && ../.venv/bin/python make_3mf.py`
Expected: prints `gimbal_head.3mf written`. If Bambu Studio isn't installed at `/Applications/BambuStudio.app`, the run fails with FileNotFoundError. Report that and leave the script in place.

- [ ] **Step 4: Run the suite**

Run: `cd esp32s3cam && ../.venv/bin/python -m pytest tests -q`
Expected: all passed
