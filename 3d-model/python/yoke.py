"""
Yoke: the U that pans with the head and carries the tilt axis.

    -X arm   houses the tilt servo, shaft pointing inward along the tilt axis.
             The servo slides in from the outside; its tabs bear on the arm's
             inner wall and are screwed into it.
    +X arm   slim; holds the tilt bearing, which the printed axle pin runs
             in. It ends just above the pivot so the SD card on that side of
             the head stays reachable. It is a separate part bolted onto the
             crossbar (2 x M3 from below), so both print without supports.
    crossbar sits on the pan bearing's inner ring, keyed onto the coupler's
             stub and held by one central M2 screw; a hole in front lets the
             wires down through the pan joint.

The arms stand outside the head's widest part (the HC-SR04 eye section), so
the head can tilt through its whole range without meeting them.
"""

from math import cos, hypot, radians, sin

from build123d import *

import base
import components as c
import head
import pan
import params as p

BAR_T = pan.SOCKET_DEPTH + 3.5 * MM  # crossbar thickness: socket, a 1.7 mm floor, the screw-head counterbore
# Crossbar top to tilt axis: the head's lowest reach over its tilt range, the
# running clearance, and 0.3 mm for angles between the 2.5° samples
HEAD_DROP = head.drop_below_axis() + p.MOVE_CLR + 0.3 * MM
ARM_INNER_X = head.ARM_X
WELL_DEPTH = 4.0 * MM  # recess around the wire hole, so the head's edges never pinch the bundle
TUNNEL_Z = 1.5 * MM  # tilt-servo cable tunnel, height above the crossbar's underside
LIP_T = 1.5 * MM  # bearing seat lip, outer side of the pin arm
ARM_BOLT_CBORE = (6.0 * MM, 3.0 * MM)  # M3 head counterbore in the crossbar's underside: diameter, depth


def tilt_axis_z(pan_b: p.Bearing = p.PAN_BEARING) -> float:
    return pan.cap_top_z(pan_b) + pan.YOKE_GAP + BAR_T + HEAD_DROP


def pin_t(tilt_b: p.Bearing = p.TILT_BEARING) -> float:
    """Thickness of the +X arm"""
    return max(tilt_b.width + LIP_T, 6 * MM)


TILT_AXIS_Z = tilt_axis_z()
TILT_SERVO_LOC = Location(
    Plane(origin=(-ARM_INNER_X, 0, TILT_AXIS_Z), x_dir=(0, 0, 1), z_dir=(1, 0, 0))
)  # case top flush with the arm's inner face, body hanging down the arm
TILT_BEARING_LOC = Location((ARM_INNER_X + p.TILT_BEARING.width / 2, 0, TILT_AXIS_Z), (0, 90, 0))
PIN_ARM_TOP_Z = TILT_AXIS_Z + p.PIN_ARM_REACH



def wire_hole_xy(pan_b: p.Bearing = p.PAN_BEARING) -> tuple[float, float]:
    r = sum(base.wire_slot(pan_b)) / 2
    return r * cos(radians(p.WIRE_ANGLE)), r * sin(radians(p.WIRE_ANGLE))


def tunnel_x(tilt_b: p.Bearing = p.TILT_BEARING, pan_b: p.Bearing = p.PAN_BEARING) -> tuple[float, float]:
    """Span of the tilt-servo cable tunnel, from the -X arm's outer end to the wire hole"""
    x_left = -ARM_INNER_X - p.SERVO_H - p.FIT - p.WALL
    return x_left, wire_hole_xy(pan_b)[0]


def arm_bolts(tilt_b: p.Bearing = p.TILT_BEARING) -> list[tuple[float, float]]:
    """M3 bolts from under the crossbar into the pin arm: (x, y)"""
    return [(ARM_INNER_X + pin_t(tilt_b) / 2, sy * 4.5 * MM) for sy in (-1, 1)]


ARM_BOLTS = arm_bolts()


def cyl_x(r: float, x0: float, x1: float, z: float) -> Part:
    """Cylinder along X at height z"""
    return Pos(x0, 0, z) * Rot(0, 90, 0) * Cylinder(r, x1 - x0, align=c.MIN)


def make_yoke(pan_b: p.Bearing = p.PAN_BEARING, tilt_b: p.Bearing = p.TILT_BEARING) -> Part:
    z_cap = pan.cap_top_z(pan_b)
    z0 = z_cap + pan.YOKE_GAP
    tilt_z = tilt_axis_z(pan_b)
    servo_loc = Location(Plane(origin=(-ARM_INNER_X, 0, tilt_z), x_dir=(0, 0, 1), z_dir=(1, 0, 0)))
    half_y = p.SERVO_W / 2 + p.FIT + p.WALL
    x_left = -ARM_INNER_X - p.SERVO_H - p.FIT - p.WALL
    x_right = ARM_INNER_X + pin_t(tilt_b)

    # crossbar, widened around the wire hole and its well with 45° shoulders
    # (the yoke prints lying on its -X end, so nothing may face that way flatter than 45°)
    hx = wire_hole_xy(pan_b)[0]
    hub_y = 9.5 * MM
    hub_x0, hub_x1 = hx - 6.0 * MM, hx + 6.0 * MM
    step = hub_y - half_y
    with BuildSketch(Plane.XY.offset(z0)) as bar:
        with Locations(((x_left + x_right) / 2, 0)):
            RectangleRounded(x_right - x_left, 2 * half_y, 3 * MM)
        Polygon((hub_x0 - step, -half_y), (hub_x0, -hub_y), (hub_x1, -hub_y), (hub_x1 + step, -half_y),
                (hub_x1 + step, half_y), (hub_x1, hub_y), (hub_x0, hub_y), (hub_x0 - step, half_y), align=None)
    yoke = extrude(bar.sketch, BAR_T)
    # foot resting on the bearing's inner ring only
    r_foot = min(pan_b.bore / 2 + 1.5 * MM, pan_b.od / 2 - pan.LIP - 0.5 * MM)
    yoke += Pos(0, 0, z_cap) * Cylinder(r_foot, pan.YOKE_GAP, align=c.MIN)

    # -X arm: servo housing with a top rounded about the tilt axis
    r_top = hypot(c.servo_body_x() + p.SERVO_TAB_L / 2 + p.FIT, p.SERVO_W / 2 + p.FIT) + p.WALL
    housing = c.box(x_left, -ARM_INNER_X, -half_y, half_y, z0, tilt_z)
    housing += c.box(x_left, -ARM_INNER_X, -half_y, half_y, tilt_z, tilt_z + r_top) & cyl_x(r_top, x_left, -ARM_INNER_X, tilt_z)
    yoke += housing

    # bolts holding the pin arm, heads sunk into the underside
    for bx, by in arm_bolts(tilt_b):
        yoke -= Pos(bx, by, z0 - 1) * Cylinder(p.M3_CLEAR / 2, BAR_T + 2, align=c.MIN)
        yoke -= Pos(bx, by, z0 - 1) * Cylinder(ARM_BOLT_CBORE[0] / 2, ARM_BOLT_CBORE[1] + 1, align=c.MIN)

    # servo pocket, open to the outside; the tabs bear on the inner wall
    cx = c.servo_body_x()
    tab_face = -p.SERVO_H + p.SERVO_TAB_Z + p.SERVO_TAB_T  # in the servo frame
    body = c.box(cx - p.SERVO_L / 2 - p.FIT, cx + p.SERVO_L / 2 + p.FIT, -p.SERVO_W / 2 - p.FIT, p.SERVO_W / 2 + p.FIT, -p.SERVO_H - 20, 1)
    tabs = c.box(cx - p.SERVO_TAB_L / 2 - p.FIT, cx + p.SERVO_TAB_L / 2 + p.FIT, -p.SERVO_W / 2 - p.FIT, p.SERVO_W / 2 + p.FIT, -p.SERVO_H - 20, tab_face)
    pilots = [Pos(cx + s * p.SERVO_TAB_HOLE_PITCH / 2, 0, tab_face) * Cylinder(p.M2_PILOT / 2, 4, align=c.MIN) for s in (-1, 1)]
    yoke -= (body + tabs + pilots).moved(servo_loc)


    # socket for the coupler's stub: round over the foot, keyed above
    r_sock = pan.STUB_D(pan_b) / 2 + p.FIT
    flat_x = pan.STUB_D(pan_b) / 2 - pan.KEY_DEPTH + pan.KEY_FIT
    top = pan.stub_top_z(pan_b) + 0.3 * MM
    yoke -= Pos(0, 0, z_cap - 0.1) * Cylinder(r_sock, 0.9, align=c.MIN)
    keyed = Pos(0, 0, z_cap) * Cylinder(r_sock, top - z_cap, align=c.MIN)
    keyed &= c.box(-r_sock - 1, flat_x, -r_sock - 1, r_sock + 1, z_cap, top)
    yoke -= keyed
    yoke -= Pos(0, 0, top - 0.1) * Cylinder(p.M2_CLEAR / 2, z0 + BAR_T - top + 1, align=c.MIN)
    yoke -= Pos(0, 0, z0 + BAR_T - 1.5 * MM) * Cylinder(2.0 * MM, 2, align=c.MIN)

    # wire hole, lined up with the coupler's and under the head's exit,
    # sunk in a well so the head's edges never pinch the bundle
    hx, hy = wire_hole_xy(pan_b)
    yoke -= Pos(0, 0, z_cap - 1) * extrude(pan.wire_hole_sketch(pan_b), BAR_T + 3)
    yoke -= c.box(hx - 4.5, hx + 4.5, hy - 8, hy + 8, z0 + BAR_T - WELL_DEPTH, z0 + BAR_T + 1)
    # tunnel through the crossbar for the tilt servo's cable (and its plug)
    tx0, tx1 = tunnel_x(tilt_b, pan_b)
    half_w = p.PLUG_W / 2 + 0.45 * MM
    yoke -= c.box(tx0 - 1, tx1, hy - half_w, hy + half_w, z0 + TUNNEL_Z, z0 + TUNNEL_Z + p.PLUG_T + 1.0 * MM)
    return yoke


def make_pin_arm(tilt_b: p.Bearing = p.TILT_BEARING, pan_b: p.Bearing = p.PAN_BEARING) -> Part:
    """The slim +X arm: a post standing on the crossbar's end, with the tilt
    bearing's seat (pressed in from the head side, lip on the outside)"""
    z_base = pan.cap_top_z(pan_b) + pan.YOKE_GAP + BAR_T
    tilt_z = tilt_axis_z(pan_b)
    x_right = ARM_INNER_X + pin_t(tilt_b)
    r_boss = tilt_b.od / 2 + 2 * MM  # = PIN_ARM_REACH for the default bearing
    arm = c.box(ARM_INNER_X, x_right, -r_boss, r_boss, z_base, tilt_z) + cyl_x(r_boss, ARM_INNER_X, x_right, tilt_z)
    arm -= cyl_x((tilt_b.od + p.PRESS) / 2, ARM_INNER_X - 0.1, ARM_INNER_X + tilt_b.width, tilt_z)
    arm -= cyl_x(tilt_b.od / 2 - LIP_T, ARM_INNER_X, x_right + 1, tilt_z)
    for bx, by in arm_bolts(tilt_b):
        arm -= Pos(bx, by, z_base - 1) * Cylinder(2.5 * MM / 2, 11, align=c.MIN)  # M3 tapped into plastic
    return arm
