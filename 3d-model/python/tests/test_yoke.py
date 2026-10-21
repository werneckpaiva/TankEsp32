import pytest
from build123d import Location, Vector

import components as c
import pan
import params as p
import yoke


@pytest.fixture(scope="module")
def y():
    return yoke.make_yoke()


def test_valid(y):
    assert y.is_valid and len(y.solids()) == 1


def test_tilt_servo_in_minus_x_arm(y):
    s = c.mg90s().moved(yoke.TILT_SERVO_LOC)
    assert (s & y).volume < 0.01
    assert s.bounding_box().max.X < 0


def test_tilt_servo_shaft_on_tilt_axis():
    shaft_tip = (yoke.TILT_SERVO_LOC * Location((0, 0, p.SERVO_SHAFT_H))).position
    assert (shaft_tip.Y, shaft_tip.Z) == pytest.approx((0, yoke.TILT_AXIS_Z), abs=1e-6)
    assert shaft_tip.X > yoke.TILT_SERVO_LOC.position.X  # points inward (+X)


@pytest.fixture(scope="module")
def arm():
    return yoke.make_pin_arm()


def test_pin_arm_bolts_to_the_crossbar(y, arm):
    assert arm.is_valid and len(arm.solids()) == 1
    assert (arm & y).volume < 0.01  # they touch, never overlap
    for sy in (-1, 1):  # bolt holes line up through both parts
        x, yy = yoke.ARM_BOLTS[0][0], sy * abs(yoke.ARM_BOLTS[0][1])
        assert not y.is_inside(Vector(x, yy, pan.YOKE_Z0 + 1))
        assert not arm.is_inside(Vector(x, yy, pan.YOKE_Z0 + yoke.BAR_T + 3))
        assert arm.is_inside(Vector(x + 1.8, yy, pan.YOKE_Z0 + yoke.BAR_T + 3))


def test_tilt_bearing_in_plus_x_arm(arm):
    y = arm
    brg = c.bearing(p.TILT_BEARING).moved(yoke.TILT_BEARING_LOC)
    assert (brg & y).volume < 0.01
    assert yoke.TILT_BEARING_LOC.position.X > 0
    assert yoke.TILT_BEARING_LOC.position.Z == pytest.approx(yoke.TILT_AXIS_Z)
    # seated: arm material just outside the bearing's rim
    pos = yoke.TILT_BEARING_LOC.position
    assert y.is_inside(Vector(pos.X, 0, pos.Z + p.TILT_BEARING.od / 2 + 0.8))


def test_pin_arm_stops_near_pivot():
    # leaves the SD card (above the pivot on the +X side) uncovered
    assert yoke.PIN_ARM_TOP_Z <= yoke.TILT_AXIS_Z + p.TILT_BEARING.od / 2 + p.WALL + 0.01


def test_arms_outside_head_width():
    assert yoke.ARM_INNER_X >= p.SR_W / 2 + p.FIT + p.HEAD_WALL + p.MOVE_CLR - 1e-6


def test_sits_on_bearing_inner_ring(y):
    # yoke reaches down to the cap top only inside the bearing's inner-ring radius
    assert y.bounding_box().min.Z == pytest.approx(pan.CAP_TOP_Z, abs=1e-6)
    assert not y.is_inside(Vector(p.PAN_BEARING.od / 2 - 1.0, 0, pan.CAP_TOP_Z + 0.3))


def test_socket_takes_stub(y):
    assert (pan.make_pan_coupler() & y).volume < 0.01


def test_wire_hole_at_wire_angle(y):
    import math
    import base
    r = sum(base.wire_slot()) / 2
    a = math.radians(p.WIRE_ANGLE)
    assert not y.is_inside(Vector(r * math.cos(a), r * math.sin(a), pan.YOKE_Z0 + 1))


def test_servo_cable_tunnel_open(y):
    x0, x1 = yoke.tunnel_x()
    z = pan.YOKE_Z0 + yoke.TUNNEL_Z + p.PLUG_T / 2
    for k in range(6):
        x = x0 + (x1 - x0) * (k + 0.5) / 6
        for yy in (-p.PLUG_W / 2 + 0.3, 0, p.PLUG_W / 2 - 0.3):
            assert not y.is_inside(Vector(x, yy, z)), (x, yy)


def test_other_bearings_build():
    assert yoke.make_yoke(p.Bearing(25, 37, 7), p.Bearing(5, 16, 5)).is_valid


def test_screw_head_has_a_floor(y):
    # plastic between the stub socket and the counterbore for the central screw's head
    socket_top = pan.stub_top_z() + 0.3
    for dz in (0.2, 0.8, 1.4):
        assert y.is_inside(Vector(1.6, 0, socket_top + dz)), dz
