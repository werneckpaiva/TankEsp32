"""
Base: the plate that screws to the tank cover, and the drum-shaped neck that
houses the pan servo. One printed part.

The plate keeps the reference gimbal's footprint and M2 hole pattern. The
neck flares out from the plate into a round drum: it has to clear the servo's
mounting tabs and the horn coupler sweeping above it. The servo stands on the
plate, held by its two tab screws (front pillar, rear ledge off the wall).
Its cable leaves the shaft end of the body, at the bottom: it runs forward
through an arch in the front pillar and down the plate's front cable hole,
next to the wires from the head.
The four plate screws are driven from above through the open drum before
the servo goes in.

This module also holds the vertical stack of the pan axis (servo, horn,
coupler, bearing), which the neck cap and yoke build on.
"""

from math import hypot, radians, tan

from build123d import *

import components as c
import params as p

# ------------------------------------------------------- pan stack (heights)
SERVO_BOTTOM_Z = p.BASE_PLATE_T
CASE_TOP_Z = SERVO_BOTTOM_Z + p.SERVO_H
HORN_Z0 = CASE_TOP_Z + 0.5 * MM  # horn hub face seated on the spline
HORN_Z1 = HORN_Z0 + p.HORN_HUB_H
COUPLER_Z0 = HORN_Z1 - p.HORN_ARM_T - 0.6 * MM  # coupler grips the arms and the hub top
COUPLER_Z1 = HORN_Z1 + 1.5 * MM
NECK_TOP_Z = COUPLER_Z0 - 1.0 * MM  # neck / neck-cap split plane
TAB_Z0 = SERVO_BOTTOM_Z + p.SERVO_TAB_Z  # tab underside

# Cable pass-through in the plate, in front of the servo (bundle from the head)
CABLE_HOLE = (10.0 * MM, 6.0 * MM)
CABLE_HOLE_XY = (0.0, 14.5 * MM)
ARCH = (p.PLUG_W + 0.9 * MM, p.PLUG_T + 1.0 * MM)  # tunnel under the front pillar for the servo cable: width, height
CAP_SCREW_R = 22.2 * MM  # neck cap screws, at 45° + n·90°
CAP_SCREW_ANGLES = (45, 135, 225, 315)


# ------------------------------------------------------------ pan stack (radii)
def wire_slot(b: p.Bearing = p.PAN_BEARING) -> tuple[float, float]:
    """Inner/outer radius of the ring where the wires cross the pan joint;
    wide enough for a servo plug to pass on its side"""
    r0 = b.od / 2 + 1.6 * MM + 0.5 * MM  # outside the bearing seat wall
    return r0, r0 + p.PLUG_T + 2 * p.FIT + 2.0 * MM


def coupler_r(b: p.Bearing = p.PAN_BEARING) -> float:
    """Radius of the horn coupler disc (it also carries the wire hole)"""
    horn = p.HORN_ARM_L + p.HORN_ARM_W_TIP / 2 + p.FIT + 1.2 * MM
    r0, r1 = wire_slot(b)
    return max(horn, r1 + 1.2 * MM)


def tab_reach() -> float:
    """Farthest point of the servo tabs from the shaft axis"""
    return hypot(p.SERVO_TAB_L / 2 + abs(c.servo_body_x()), p.SERVO_W / 2)


def drum_radii(b: p.Bearing = p.PAN_BEARING) -> tuple[float, float]:
    """Inner and outer radius of the neck drum"""
    r_in = max(tab_reach() + p.FIT, coupler_r(b) + p.MOVE_CLR, wire_slot(b)[1] + 1 * MM)
    return r_in, r_in + 1.6 * MM


def pan_servo_loc(long_axis: str = p.BASE_LONG_AXIS) -> Location:
    """mg90s() frame in the world: shaft on the pan axis, body along the plate's long side"""
    loc = Location((0, 0, CASE_TOP_Z), (0, 0, 90))  # body extends toward -Y
    return Rot(0, 0, 90) * loc if long_axis == "X" else loc


PAN_SERVO_LOC = pan_servo_loc()


def make_base(long_axis: str = p.BASE_LONG_AXIS) -> Part:
    r_in, r_out = drum_radii()
    # flare from the plate outline to the drum, inside and out no flatter than
    # 40° from vertical so it prints without support
    run = max(r_out - p.BASE_W / 2, r_in - (p.BASE_W / 2 - p.WALL), 1 * MM)
    cone_top = SERVO_BOTTOM_Z + run / tan(radians(40))
    assert cone_top < TAB_Z0, "the flare must reach full width below the servo tabs"

    # Plate with corner bosses
    plate = extrude(RectangleRounded(p.BASE_W, p.BASE_L, p.BASE_CORNER_R), p.BASE_PLATE_T)
    hole_xy = [(sx * p.BASE_HOLE_DX / 2, sy * p.BASE_HOLE_DY / 2) for sx in (-1, 1) for sy in (-1, 1)]
    bosses = [Pos(x, y, 0) * Cylinder(p.BASE_CBORE_D / 2 + 1.5 * MM, p.BASE_BOSS_H, align=c.MIN) for x, y in hole_xy]

    # Drum: flare from the plate outline to a circle, then straight up
    def flare(inset: float, r: float) -> Part:
        bottom = Plane.XY.offset(p.BASE_PLATE_T) * RectangleRounded(
            p.BASE_W - 2 * inset, p.BASE_L - 2 * inset, max(p.BASE_CORNER_R - inset, 0.5 * MM)
        )
        top = Plane.XY.offset(cone_top) * Circle(r)
        return loft([bottom, top]) + Pos(0, 0, cone_top) * Cylinder(r, NECK_TOP_Z - cone_top, align=c.MIN)

    outside = flare(0, r_out)
    drum = outside - (flare(p.WALL, r_in) + Pos(0, 0, NECK_TOP_Z - 1) * Cylinder(r_in, 2, align=c.MIN))

    # Servo tab supports: a pillar under the front tab, a ledge off the rear wall
    # (the servo frame is turned 90°, so its x becomes world y)
    front_y, rear_y = (c.servo_body_x() + s * p.SERVO_TAB_HOLE_PITCH / 2 for s in (1, -1))
    body_front = c.servo_body_x() + p.SERVO_L / 2 + p.FIT
    body_rear = c.servo_body_x() - p.SERVO_L / 2 - p.FIT
    # the pillar straddles the servo's cable: two legs and a roof the tab screw goes into
    half = ARCH[0] / 2 + 1.6 * MM
    pillar = c.box(-half, half, body_front, front_y + 2.2 * MM, p.BASE_PLATE_T, TAB_Z0)
    pillar -= c.box(-ARCH[0] / 2, ARCH[0] / 2, body_front - 1, front_y + 3.2 * MM, p.BASE_PLATE_T - 1, p.BASE_PLATE_T + ARCH[1])
    with BuildSketch(Plane.YZ) as ledge_profile:
        Polygon(
            (-r_out + 0.5, TAB_Z0 - 3 - (r_out - 0.5 + body_rear)),
            (-r_out + 0.5, TAB_Z0),
            (body_rear, TAB_Z0),
            (body_rear, TAB_Z0 - 3),
            align=None,
        )
    ledge = extrude(ledge_profile.sketch, 3, both=True) & outside  # its foot grows out of the wall, not out past it

    # Neck-cap screw bosses just under the split plane
    cap_bosses = []
    for a in CAP_SCREW_ANGLES:
        boss = Pos(0, 0, NECK_TOP_Z - 7) * Cylinder(2.2 * MM, 7, align=c.MIN)
        # the cone's tip reaches into the wall so it starts on it, not in mid-air
        boss += Pos(0, 0, NECK_TOP_Z - 10) * Cone(1.0 * MM, 2.2 * MM, 3, align=c.MIN)
        cap_bosses.append(Rot(0, 0, a) * Pos(CAP_SCREW_R, 0, 0) * boss)

    part = plate + bosses + drum + pillar + ledge + cap_bosses

    # Holes
    for x, y in hole_xy:
        part -= Pos(x, y, 0) * Cylinder(p.BASE_HOLE_D / 2, 3 * p.BASE_BOSS_H)
        part -= Pos(x, y, p.BASE_BOSS_H - p.BASE_CBORE_DEPTH) * Cylinder(p.BASE_CBORE_D / 2, NECK_TOP_Z, align=c.MIN)
    part -= Pos(*CABLE_HOLE_XY, 0) * Box(*CABLE_HOLE, 3 * p.BASE_PLATE_T)
    for y in (front_y, rear_y):
        part -= Pos(0, y, TAB_Z0) * Cylinder(p.M2_PILOT / 2, 16, align=(Align.CENTER, Align.CENTER, Align.MAX))
    for a in CAP_SCREW_ANGLES:
        part -= Rot(0, 0, a) * Pos(CAP_SCREW_R, 0, NECK_TOP_Z) * Cylinder(p.M2_PILOT / 2, 8, align=(Align.CENTER, Align.CENTER, Align.MAX))

    return Rot(0, 0, 90) * part if long_axis == "X" else part
