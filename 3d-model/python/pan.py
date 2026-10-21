"""
Pan joint parts above the servo: the neck cap with the pan bearing, the horn
coupler with its stub shaft, and a printed bushing that can stand in for the
bearing.

Load path: the yoke is screwed onto the coupler's stub, clamping the bearing's
inner ring between the yoke and the coupler; the bearing's outer ring sits in
the neck cap, which is screwed to the neck. Weight and tipping loads go
through the bearing into the neck; the servo only turns the coupler.

Wires: they drop from the yoke through an arc slot in the cap's ceiling
(centred on WIRE_ANGLE, long enough to follow ±90° of pan plus a margin) and
through a hole in the coupler, which turns with the yoke, so they never rub
on a moving part.

Assembly:
    1. Press the bearing (or bushing) into the cap from the top.
    2. Push the coupler's stub up through the bearing from below.
    3. Press the servo horn into the coupler's pocket.
    4. Centre the pan servo, then lower cap + coupler onto the neck so the
       horn slides onto the spline, with the coupler's wire hole toward -X.
    5. Screw the cap to the neck (4 x M2 x 16).
    6. Put the yoke on the stub and fix it with the central M2 screw.
"""

from math import degrees, pi

from build123d import *

import base
import components as c
import params as p

BEARING_Z0 = base.COUPLER_Z1 + 1.5 * MM  # spacer under the inner ring; the seat lip sits beside it
LIP_STEP = 0.6 * MM  # flat step the bearing's outer ring sits on
LIP_T = 1.0 * MM  # lip thickness; below the step it slopes inward at 45°
LIP = LIP_STEP + LIP_T  # how far the lip reaches in under the outer ring, at its deepest
CEILING_T = 3.0 * MM  # the bearing seat hangs from it
YOKE_GAP = 1.0 * MM  # between the cap top and the yoke
SOCKET_DEPTH = 6.0 * MM  # stub length inside the yoke
HORN_ANGLE = p.WIRE_ANGLE + 90  # horn arms run across the wire direction, clear of the hole
KEY_DEPTH = 2.0 * MM  # flat on the stub that keys the yoke
KEY_FIT = 0.1 * MM  # clearance on the key's flat face


def STUB_D(b: p.Bearing) -> float:
    return b.bore - 0.1 * MM


def cap_top_z(b: p.Bearing = p.PAN_BEARING) -> float:
    return BEARING_Z0 + b.width


def pan_bearing_loc(b: p.Bearing = p.PAN_BEARING) -> Location:
    return Location((0, 0, BEARING_Z0 + b.width / 2))


def stub_top_z(b: p.Bearing = p.PAN_BEARING) -> float:
    return cap_top_z(b) + YOKE_GAP + SOCKET_DEPTH


PAN_BEARING_LOC = pan_bearing_loc()
CAP_TOP_Z = cap_top_z()
YOKE_Z0 = CAP_TOP_Z + YOKE_GAP  # underside of the yoke
WIRE_SLOT_Z = CAP_TOP_Z - CEILING_T / 2


def wire_arc(b: p.Bearing, core_half: float) -> Sketch:
    """Slot on the wire ring, centred on WIRE_ANGLE, its end centres ±core_half apart"""
    r0, r1 = base.wire_slot(b)
    arc = CenterArc((0, 0), (r0 + r1) / 2, p.WIRE_ANGLE - core_half, 2 * core_half)
    return Sketch() + SlotArc(arc, r1 - r0)


def _hole_core_half(b: p.Bearing) -> float:
    """Half angle between the end centres of a wire hole big enough for the bundle"""
    r0, r1 = base.wire_slot(b)
    w, r_mid = r1 - r0, (r0 + r1) / 2
    need = 1.02 * p.WIRE_COUNT * p.WIRE_D**2 / p.WIRE_FILL  # 2% over, so rounding never lands short
    length = max(p.PLUG_W + 1.5 * MM, (need - pi * w**2 / 4) / w + w)
    return degrees((length - w) / 2 / r_mid)


def hole_half_angle(b: p.Bearing = p.PAN_BEARING) -> float:
    """Half angle a wire hole covers, end to end"""
    r0, r1 = base.wire_slot(b)
    return _hole_core_half(b) + degrees((r1 - r0) / 2 / ((r0 + r1) / 2))


def wire_hole_sketch(b: p.Bearing = p.PAN_BEARING) -> Sketch:
    """The hole the wires take through the coupler and the yoke (they turn together)"""
    return wire_arc(b, _hole_core_half(b))


def make_neck_cap(b: p.Bearing = p.PAN_BEARING) -> Part:
    z0, z1 = base.NECK_TOP_Z, cap_top_z(b)
    r_out = base.drum_radii(b)[1]
    r_in = base.coupler_r(b) + p.MOVE_CLR
    shell = Pos(0, 0, z0) * Cylinder(r_out, z1 - z0, align=c.MIN)
    shell -= Pos(0, 0, z0) * Cylinder(r_in, z1 - z0 - CEILING_T, align=c.MIN)
    # bearing seat hanging from the ceiling, with a lip under the outer ring
    seat_z0 = BEARING_Z0 - LIP_T
    shell += Pos(0, 0, seat_z0) * Cylinder(b.od / 2 + 1.6 * MM, z1 - seat_z0, align=c.MIN)
    shell -= Pos(0, 0, BEARING_Z0) * Cylinder((b.od + p.PRESS) / 2, b.width + 1, align=c.MIN)
    # the lip: a narrow flat step for the bearing, then a 45° slope inward. The
    # cap prints upside down, so a flat ledge here would start in mid-air
    shell -= Pos(0, 0, seat_z0) * Cone(b.od / 2 - LIP, b.od / 2 - LIP_STEP, LIP_T, align=c.MIN)
    shell -= Pos(0, 0, seat_z0 - 1) * Cylinder(b.od / 2 - LIP, 1.01, align=c.MIN)
    # wire slot following the hole through ±90° of pan, with a margin at each end
    half = (p.PAN_RANGE[1] - p.PAN_RANGE[0]) / 2 + _hole_core_half(b) + p.SLOT_MARGIN
    shell -= Pos(0, 0, z1 - CEILING_T - 1) * extrude(wire_arc(b, half), CEILING_T + 2)
    # screws into the neck, heads sunk into the ceiling
    for a in base.CAP_SCREW_ANGLES:
        at = Rot(0, 0, a) * Pos(base.CAP_SCREW_R, 0, 0)
        shell -= at * Pos(0, 0, z0 - 1) * Cylinder(p.M2_CLEAR / 2, z1 - z0 + 2, align=c.MIN)
        shell -= at * Pos(0, 0, z1 - 1.6 * MM) * Cylinder(2.0 * MM, 2, align=c.MIN)
    return shell


def coupler_outline(b: p.Bearing = p.PAN_BEARING) -> Part:
    """Solid envelope of the coupler disc (before the pocket and hole)"""
    return Pos(0, 0, base.COUPLER_Z0) * Cylinder(base.coupler_r(b), base.COUPLER_Z1 - base.COUPLER_Z0, align=c.MIN)


def make_pan_coupler(b: p.Bearing = p.PAN_BEARING) -> Part:
    disc = coupler_outline(b)
    # horn pocket, open at the bottom so the horn presses in from below
    pocket = Pos(0, 0, base.COUPLER_Z0 - 1) * Cylinder(p.HORN_HUB_D / 2 + p.FIT, base.HORN_Z1 - base.COUPLER_Z0 + 1, align=c.MIN)
    arm_top = base.HORN_Z1 + p.FIT
    pocket += Pos(0, 0, base.COUPLER_Z0 - 1) * Rot(0, 0, HORN_ANGLE) * extrude(c.horn_arms_sketch(p.FIT), arm_top - base.COUPLER_Z0 + 1)
    disc -= pocket
    # wire hole, turning with the yoke
    disc -= Pos(0, 0, base.COUPLER_Z0 - 1) * extrude(wire_hole_sketch(b), 10)
    # spacer under the bearing's inner ring, then the stub up into the yoke
    disc += Pos(0, 0, base.COUPLER_Z1) * Cylinder(min(b.bore / 2 + 1.5 * MM, b.od / 2 - LIP - 0.5), BEARING_Z0 - base.COUPLER_Z1, align=c.MIN)
    stub = Pos(0, 0, BEARING_Z0) * Cylinder(STUB_D(b) / 2, stub_top_z(b) - BEARING_Z0, align=c.MIN)
    # flat on the part above the bearing keys the yoke
    flat_x = STUB_D(b) / 2 - KEY_DEPTH
    stub -= c.box(flat_x, STUB_D(b), -STUB_D(b), STUB_D(b), cap_top_z(b) + 0.5, stub_top_z(b) + 1)
    stub -= Pos(0, 0, stub_top_z(b)) * Cylinder(p.M2_PILOT / 2, 8, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return disc + stub


def make_bushing(b: p.Bearing) -> Part:
    """Printed stand-in for a bearing: same outside, sliding fit inside. It is
    0.6 mm shorter so the parts turning on it bottom out before clamping it"""
    h = b.width - 0.6 * MM
    return Cylinder(b.od / 2, h) - Cylinder(b.bore / 2 + p.FIT, h)
