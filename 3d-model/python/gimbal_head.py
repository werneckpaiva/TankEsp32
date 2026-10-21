"""
Wall-E style camera head on a pan/tilt gimbal for an RC tank: an ESP32-S3-CAM,
an HC-SR04 (the "eyes") and an SYD1230 laser all aim together, panned and
tilted by two MG90S servos running on ball bearings. Design: AGENTS.md.

Frames:
    World: origin on the pan axis at the bottom of the base plate, +Y forward
    (camera direction at rest), +Z up, +X to the right seen from behind.
    Head: origin on the tilt axis between the yoke arms, same axes at rest.
    Positive pan turns toward +X; positive tilt looks up. Range: pan ±90°,
    tilt -45° (down) to +90° (up).

Printed parts (STL files written to ../stl/):
    gimbal_base.stl         plate (reference gimbal footprint) + drum neck
    gimbal_neck_cap.stl     holds the pan bearing, wire slot over the front
    gimbal_pan_coupler.stl  takes the pan servo horn; its stub carries the yoke
    gimbal_yoke.stl         crossbar and the -X arm holding the tilt servo
    gimbal_pin_arm.stl      the slim +X arm with the tilt bearing (bolts on)
    gimbal_head_front.stl   face, eyes, camera, laser clamp, side joints
    gimbal_head_rear.stl    back cover
    gimbal_brows.stl        the two brow tubes around the eyes (seat on the face)
    gimbal_tilt_axle.stl    the tilt axle pin (through the tilt bearing into the head)
    gimbal_fit_test.stl     optional test piece: just the face with the board pins,
                            HC-SR04 ribs and openings, to check the fit quickly
    gimbal_pan_bushing.stl / gimbal_tilt_bushing.stl
                            only when USE_PAN_BEARING / USE_TILT_BEARING is
                            False in params.py: printed stand-ins

Bought parts and hardware:
    2 x MG90S servo (with their double-arm horns and tab screws; tab screws
      no longer than 6 mm, or they reach through the yoke arm into the head)
    2 x 608 bearing (pan and tilt), or the printed bushings
    ESP32-S3-CAM, HC-SR04, SYD1230 laser, Dupont jumper wires
    1 x M3 x 25 bolt + nut + washer: through the tilt axle pin, nut inside the head
    4 x M2 x 16: neck cap to neck
    1 x M2 x 8: yoke to coupler stub
    2 x M3 x 12: pin arm to the crossbar (from below)
    2 x M2 x 8: rear cover, bottom (from behind)
    2 x M2 x 6: rear cover, top (from above, through the head's top wall)
    1 x M2 x 10: laser clamp
    4 x M2 x 6: HC-SR04 to its corner posts (through its corner holes)
    2 x M2 x 6: camera board, at the two corners without a pin
    4 x M2: base plate to the tank cover (length to suit the cover)

Assembly:
    1. Screw the base to the tank cover through the open drum.
    2. Pan servo: its cable leaves the shaft end. Thread the plug through the
       arch at the bottom of the front pillar and down the plate's front
       cable hole, stand the servo on the plate with the shaft centred, and
       screw its tabs to the front pillar and the rear ledge.
    3. Neck cap: press in the 608. Set the horn on the centred pan servo's
       spline, arms across the -X direction. Push the coupler's stub up through
       the bearing from below, then lower cap + coupler onto the neck so the
       horn drops into the coupler's pocket, with the coupler's wire hole
       toward -X. Screw the cap down (4 x M2 x 16).
    4. Yoke: fit it on the stub (the flat keys it) and fix it with the
       central M2 x 8. Press a 608 into the pin arm from its inner side and
       bolt the arm onto the crossbar's +X end (2 x M3 x 12 from below).
    5. Head: fit the camera board on its two pins (camera through the face,
       USB-C down) and screw its other two corners to their standoffs with
       2 x M2 x 6, so it can't slide back. Slide the HC-SR04 in from the back, cans first, until
       its board rests on the four corner posts (the cans stand out through
       the face), and screw it to them: 4 x M2 x 6 through its corner holes.
       Seat the brow tubes in the recesses around the eye openings, over the
       cans (a drop of glue holds them).
       Push the laser into its clamp; aim it later, then tighten the clamp.
    6. Wires: plug in the Dupont leads inside the head and pass them out of
       the slot in the head's underside (on the -X side).
    7. Tilt joint: press the tilt servo's horn into the pocket on the head's
       -X side, arms tilted as the pocket shows. Hold the head between the
       arms, push the axle pin from outside through the 608 into the head's
       socket, and bolt it (M3 x 25 from outside, washer and nut inside the
       head, reached through the open back). Centre the tilt servo, level the
       head, and slide the servo into the -X arm from outside so its spline
       enters the horn; screw its tabs. Close the head with the rear cover:
       its rim drops inside the head's opening and lines it up, then 2 x M2 x 8
       at the bottom from behind and 2 x M2 x 6 through the top wall.
    8. Run the tilt servo's cable down the -X arm into the tunnel in the
       crossbar. Feed it and the head's bundle down the yoke's wire hole (in
       the well, under the head's exit), through the cap's slot and the
       coupler's hole, and out of the base through the plate's front hole.
       Leave the slack in the drum: the bundle slides through the holes as
       the head tilts.

Viewing:
    1. Start the viewer (from the build123d environment) and leave it running:
           ocp-viewer
       then open http://localhost:3939 (or use the OCP CAD Viewer panel in
       VS Code).
    2. From this folder (python/) run:
           python gimbal_head.py
       It checks the motion range, writes the STL files and shows the
       assembly at rest (head semi-transparent). Without a viewer it still
       writes the STLs. To show another pose, give the angles in degrees:
           python gimbal_head.py --pan 45 --tilt -30
       --pan from -90 to 90 (positive turns right, toward +X), --tilt from
       -45 to 90 (positive looks up); both default to 0.

Printing (Bambu A1, PLA, 0.4 mm nozzle); make_3mf.py builds a sliced project:
    neck cap (upside down), coupler, rear cover, brows, bushings, pin arm
    (on its outer face), head front (face down): no support. Base (upright)
    and yoke (lying on the servo arm's outer face): tree supports from the plate, for
    the few spots the slicer flags. Brims on the yoke and the tilt axle pin.
    Bushings: with USE_*_BEARING = False they stand in for the bearings; do
    not overtighten the M3 tilt axle on a bushing, it clamps it.

Electronics notes (not part of the print):
    - HC-SR04 Echo is 5 V: put a divider (e.g. 1k / 2k) before the ESP32 input.
    - Laser draws ~30-40 mA: switch it with a transistor/MOSFET module.
    - Power the servos from a separate 5 V supply (~1 A), grounds shared.
    - Measure your parts and correct params.py; everything rebuilds from it.
"""

import argparse
from functools import cache
from pathlib import Path
from typing import Callable

from build123d import *
from ocp_viewer import show

import base
import components as c
import head
import pan
import params as p
import yoke

ROOT = Path(__file__).resolve().parent.parent  # the 3d-model/ folder
STL_DIR = ROOT / "stl"  # written here, read by make_3mf.py
THREEMF_DIR = ROOT / "3mf"

STATIC = {"base", "neck_cap", "pan_servo", "pan_bearing"}
PANNING = {"yoke", "pin_arm", "pan_coupler", "tilt_servo", "tilt_bearing"}
TILTING = {"head_front", "head_rear", "brows", "tilt_axle", "board", "hcsr04", "laser"}


@cache
def _parts() -> dict[str, Part]:
    """Every part in its own frame (world for static, pan-0 for panning, head frame for tilting)"""
    pan_brg = c.bearing(p.PAN_BEARING) if p.USE_PAN_BEARING else pan.make_bushing(p.PAN_BEARING)
    tilt_brg = c.bearing(p.TILT_BEARING) if p.USE_TILT_BEARING else pan.make_bushing(p.TILT_BEARING)
    return {
        "base": base.make_base(),
        "neck_cap": pan.make_neck_cap(),
        "pan_servo": c.mg90s().moved(base.PAN_SERVO_LOC),
        "pan_bearing": pan_brg.moved(pan.PAN_BEARING_LOC),
        "yoke": yoke.make_yoke(),
        "pin_arm": yoke.make_pin_arm(),
        "pan_coupler": pan.make_pan_coupler(),
        "tilt_servo": c.mg90s().moved(yoke.TILT_SERVO_LOC),
        "tilt_bearing": tilt_brg.moved(yoke.TILT_BEARING_LOC),
        "head_front": head.make_head_front(),
        "head_rear": head.make_head_rear(),
        "brows": head.make_brows(mounted=True),
        "tilt_axle": head.make_tilt_axle(mounted=True),
        "board": c.esp32_board().moved(head.BOARD_LOC),
        "hcsr04": c.hcsr04().moved(head.SR04_LOC),
        "laser": c.laser().moved(head.LASER_LOC),
    }


def pan_location(pan_deg: float) -> Location:
    """Positive pan turns the camera toward +X"""
    return Location((0, 0, 0), (0, 0, -pan_deg))


def head_to_world(pan_deg: float, tilt_deg: float) -> Location:
    """Head frame in the world; positive tilt looks up"""
    return pan_location(pan_deg) * Location((0, 0, yoke.TILT_AXIS_Z)) * Location((0, 0, 0), (tilt_deg, 0, 0))


def place(pan_deg: float, tilt_deg: float) -> dict[str, Part]:
    placed = {}
    for name, part in _parts().items():
        if name in TILTING:
            placed[name] = part.moved(head_to_world(pan_deg, tilt_deg))
        elif name in PANNING:
            placed[name] = part.moved(pan_location(pan_deg))
        else:
            placed[name] = part
    return placed


def joint_zone(pan_deg: float) -> Part:
    """Where head and yoke touch on purpose: around the tilt axis at each arm"""
    x_in = yoke.ARM_INNER_X - 4 * MM
    servo_side = Pos(-x_in, 0, yoke.TILT_AXIS_Z) * Rot(0, -90, 0) * Cylinder(p.HORN_ARM_L + 2 * MM, 40, align=c.MIN)
    pin_side = Pos(x_in, 0, yoke.TILT_AXIS_Z) * Rot(0, 90, 0) * Cylinder(p.TILT_BEARING.od / 2 + 2 * MM, 20, align=c.MIN)
    return (servo_side + pin_side).moved(pan_location(pan_deg))


def _fuse(parts: dict[str, Part], names: set[str]) -> Part:
    out = None
    for n in sorted(names):
        out = parts[n] if out is None else out + parts[n]
    return out


def run_checks() -> None:
    """Sweep the joints and assert nothing collides"""
    tilts = list(range(p.TILT_RANGE[0], p.TILT_RANGE[1] + 1, 15)) + [p.TILT_RANGE[1]]
    for pan_deg in (p.PAN_RANGE[0], 0, p.PAN_RANGE[1]):
        for tilt_deg in tilts:
            parts = place(pan_deg, tilt_deg)
            moving = _fuse(parts, TILTING)
            fixed = _fuse(parts, PANNING | STATIC)
            clash = (moving & fixed).volume
            assert clash < 0.01, f"head hits the yoke/base at pan {pan_deg}°, tilt {tilt_deg}°: {clash:.2f} mm³"
            gap = (moving - joint_zone(pan_deg)).distance_to(
                _fuse(parts, (PANNING | STATIC) - {"tilt_servo", "tilt_bearing"}) - joint_zone(pan_deg)
            )
            assert gap >= p.MOVE_CLR - 1e-3, f"head only {gap:.2f} mm from the yoke/base at pan {pan_deg}°, tilt {tilt_deg}°"
        swinging = _fuse(parts, (PANNING | TILTING) - {"pan_coupler"})
        assert swinging.distance_to(parts["base"]) >= p.MOVE_CLR - 1e-3, f"pan {pan_deg}° rubs the base"
    print(f"motion checks passed: pan {p.PAN_RANGE}, tilt {p.TILT_RANGE}")


# ------------------------------------------------------------------ printing
# Rotation that puts each part in its print orientation
PRINT_ROT = {
    "base": Rot(0, 0, 0),
    "neck_cap": Rot(180, 0, 0),  # ceiling on the bed
    "pan_coupler": Rot(0, 0, 0),
    "yoke": Rot(0, -90, 0),  # on the servo arm's outer face
    "pin_arm": Rot(0, 90, 0),  # on its outer face; the bearing seat prints round
    "head_front": Rot(-90, 0, 0),  # face down
    "head_rear": Rot(90, 0, 0),  # outer face down, pegs up
    "brows": Rot(0, 0, 0),  # already flat: tube end down, spigot up
    "tilt_axle": Rot(0, 0, 0),  # flange down
    "pan_bushing": Rot(0, 0, 0),
    "tilt_bushing": Rot(0, 0, 0),
}

# Parts tall for their bed contact get a brim so they stay put on the bed
NEEDS_BRIM = {"yoke", "tilt_axle"}


BUILDERS: dict[str, Callable[[], Part]] = {
    "base": base.make_base,
    "neck_cap": pan.make_neck_cap,
    "pan_coupler": pan.make_pan_coupler,
    "yoke": yoke.make_yoke,
    "pin_arm": yoke.make_pin_arm,
    "head_front": head.make_head_front,
    "head_rear": head.make_head_rear,
    "brows": head.make_brows,
    "tilt_axle": head.make_tilt_axle,
    "pan_bushing": lambda: pan.make_bushing(p.PAN_BEARING),
    "tilt_bushing": lambda: pan.make_bushing(p.TILT_BEARING),
}

# Which parts need supports (tree, from the build plate only)
NEEDS_SUPPORT = {
    "base": True,  # the slicer flags floating spots inside the drum
    "neck_cap": False,
    "pan_coupler": False,
    "yoke": True,  # short bridges would print bare, but the slicer asks for support
    "pin_arm": False,
    "head_front": False,
    "head_rear": False,
    "brows": False,
    "tilt_axle": False,
    "pan_bushing": False,
    "tilt_bushing": False,
}


def printed_parts() -> dict[str, Callable[[], Part]]:
    """Printed parts by name; reads the bearing switches at call time"""
    skip = {"pan_bushing"} if p.USE_PAN_BEARING else set()
    skip |= {"tilt_bushing"} if p.USE_TILT_BEARING else set()
    return {n: b for n, b in BUILDERS.items() if n not in skip}


def print_oriented(name: str) -> Part:
    part = PRINT_ROT[name] * BUILDERS[name]()
    bb = part.bounding_box()
    return part.moved(Location((-bb.center().X, -bb.center().Y, -bb.min.Z)))


def export_fit_test(out_dir: Path) -> Path:
    """The face-only test piece (not on the main plate): print it face down to
    check the boards fit before printing the whole head"""
    part = Rot(-90, 0, 0) * head.make_fit_test()
    bb = part.bounding_box()
    part = part.moved(Location((-bb.center().X, -bb.center().Y, -bb.min.Z)))
    path = Path(out_dir) / "gimbal_fit_test.stl"
    export_stl(part, str(path))
    return path


def export_all(out_dir: Path) -> list[Path]:
    files = []
    for name in printed_parts():
        path = Path(out_dir) / f"gimbal_{name}.stl"
        export_stl(print_oriented(name), str(path))
        files.append(path)
    return files


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Pose to show: pan and tilt in degrees, checked against the joint ranges"""
    parser = argparse.ArgumentParser(description="Check, export and show the camera head gimbal.")
    parser.add_argument("--pan", type=float, default=0.0,
                        help=f"pan angle in degrees, {p.PAN_RANGE[0]} to {p.PAN_RANGE[1]}; positive turns right (+X)")
    parser.add_argument("--tilt", type=float, default=0.0,
                        help=f"tilt angle in degrees, {p.TILT_RANGE[0]} to {p.TILT_RANGE[1]}; positive looks up")
    args = parser.parse_args(argv)
    for name, value, (lo, hi) in (("pan", args.pan, p.PAN_RANGE), ("tilt", args.tilt, p.TILT_RANGE)):
        if not lo <= value <= hi:
            parser.error(f"--{name} {value:g} is outside the joint's range {lo} to {hi}")
    return args


if __name__ == "__main__":
    args = parse_args()
    run_checks()
    STL_DIR.mkdir(exist_ok=True)
    for f in export_all(STL_DIR):
        print(f"wrote {f.name}")
    print(f"wrote {export_fit_test(STL_DIR).name} (test piece, print it on its own)")
    parts = place(args.pan, args.tilt)
    print(f"showing pan {args.pan:g}°, tilt {args.tilt:g}°")
    colors = {
        "base": "gray", "neck_cap": "gray", "pan_coupler": "orange", "yoke": "orange", "pin_arm": "orange",
        "head_front": "gold", "head_rear": "gold", "brows": "gold", "tilt_axle": "orange", "board": "green", "hcsr04": "royalblue",
        "laser": "goldenrod", "pan_servo": "steelblue", "tilt_servo": "steelblue",
        "pan_bearing": "silver", "tilt_bearing": "silver",
    }
    names = list(parts)
    try:
        show(
            *parts.values(),
            names=names,
            colors=[colors[n] for n in names],
            alphas=[0.5 if n.startswith("head") else 1 for n in names],
        )
    except Exception as e:
        print(f"viewer unavailable ({e}); STL files written")
