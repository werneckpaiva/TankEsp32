import math

import pytest
from build123d import Location, Vector

import base
import components as c
import pan
import params as p


@pytest.fixture(scope="module")
def cap():
    return pan.make_neck_cap()


@pytest.fixture(scope="module")
def coupler():
    return pan.make_pan_coupler()


def test_cap_holds_bearing(cap):
    brg = c.bearing(p.PAN_BEARING).moved(pan.PAN_BEARING_LOC)
    assert cap.is_valid and (cap & brg).volume < 0.01
    # seat wall surrounds it
    r = p.PAN_BEARING.od / 2 + 0.5
    z = pan.PAN_BEARING_LOC.position.Z
    assert cap.is_inside(Vector(r + 0.5, 0, z))


def test_cap_sits_on_neck(cap):
    assert cap.bounding_box().min.Z == pytest.approx(base.NECK_TOP_Z, abs=1e-6)
    assert (cap & base.make_base()).volume < 0.01


def test_wire_window_open_over_pan_range(cap):
    # the wire slot is centred on WIRE_ANGLE and must follow ±90° of pan
    z = pan.WIRE_SLOT_Z
    radii = [p.PAN_BEARING.od / 2 + k for k in (2, 3, 4, 5)]

    def open_at(rad):
        return all(
            not cap.is_inside(Vector(rad * math.cos(math.radians(p.WIRE_ANGLE + a)), rad * math.sin(math.radians(p.WIRE_ANGLE + a)), z))
            for a in range(-90, 91, 15)
        )

    assert any(open_at(r) for r in radii)


def test_coupler_takes_horn(coupler):
    horn = c.mg90s_horn().moved(Location((0, 0, base.HORN_Z0), (0, 0, pan.HORN_ANGLE)))
    assert coupler.is_valid and (coupler & horn).volume < 0.01
    # the horn is actually gripped: its arm tips sit inside the coupler's outline
    a = math.radians(pan.HORN_ANGLE)
    tip = Vector(p.HORN_ARM_L * math.cos(a), p.HORN_ARM_L * math.sin(a), base.HORN_Z1 - p.HORN_ARM_T / 2)
    assert pan.coupler_outline().is_inside(tip)


def test_coupler_clears_servo_and_cap(coupler, cap):
    servo = c.mg90s().moved(base.PAN_SERVO_LOC)
    assert (coupler & servo).volume < 0.01
    assert coupler.distance_to(cap) >= p.MOVE_CLR - 1e-3


def test_coupler_wire_hole_at_wire_angle(coupler):
    r = sum(base.wire_slot()) / 2
    a = math.radians(p.WIRE_ANGLE)
    assert not coupler.is_inside(Vector(r * math.cos(a), r * math.sin(a), (base.COUPLER_Z0 + base.COUPLER_Z1) / 2))


def test_stub_through_bearing(coupler):
    z = pan.PAN_BEARING_LOC.position.Z
    assert coupler.is_inside(Vector(0, 0, z + 0.5))  # stub fills the bore (pilot hole is higher up)
    assert pan.STUB_D(p.PAN_BEARING) == pytest.approx(p.PAN_BEARING.bore - 0.1)
    assert coupler.bounding_box().max.Z > pan.CAP_TOP_Z


@pytest.mark.parametrize("b", [p.Bearing(8, 22, 7), p.Bearing(25, 37, 7)])
def test_other_bearing_sizes_build(b):
    assert pan.make_neck_cap(b).is_valid and pan.make_pan_coupler(b).is_valid


def test_bushing_envelope():
    bb = pan.make_bushing(p.PAN_BEARING).bounding_box()
    assert bb.size.X == pytest.approx(22, abs=0.01)
    assert not pan.make_bushing(p.PAN_BEARING).is_inside(Vector(p.PAN_BEARING.bore / 2 + p.FIT / 2, 0, 0))


def test_stub_has_one_flat(coupler):
    z = pan.CAP_TOP_Z + 3
    r = pan.STUB_D(p.PAN_BEARING) / 2 - 0.3
    assert not coupler.is_inside(Vector(r, 0, z))  # the flat (keys the yoke)
    for x, y in ((-r, 0), (0, r), (0, -r)):  # the rest of the stub is round
        assert coupler.is_inside(Vector(x, y, z)), (x, y)


def test_stub_key_has_little_play(coupler):
    import yoke
    y = yoke.make_yoke()
    turned = coupler.moved(Location((0, 0, 0), (0, 0, 2)))
    assert (turned & y).volume > 0.01  # 2° of free play at most


def test_wire_hole_sized_for_bundle_and_plug():
    hole = pan.wire_hole_sketch(p.PAN_BEARING)
    need = p.WIRE_COUNT * p.WIRE_D**2 / p.WIRE_FILL
    assert hole.area >= need
    r = sum(base.wire_slot()) / 2
    a = math.radians(p.WIRE_ANGLE)
    from build123d import Rectangle, Pos, Rot
    plug = Pos(r * math.cos(a), r * math.sin(a)) * Rot(0, 0, p.WIRE_ANGLE + 90) * Rectangle(p.PLUG_W + 0.4, p.PLUG_T + 0.4)
    assert (plug - hole).area < 1e-3


def test_cap_slot_has_end_margin(cap):
    z = pan.WIRE_SLOT_Z
    r = sum(base.wire_slot()) / 2
    half = (p.PAN_RANGE[1] - p.PAN_RANGE[0]) / 2 + pan.hole_half_angle(p.PAN_BEARING) + p.SLOT_MARGIN - 1
    for a in (p.WIRE_ANGLE - half, p.WIRE_ANGLE, p.WIRE_ANGLE + half):
        rad = math.radians(a)
        assert not cap.is_inside(Vector(r * math.cos(rad), r * math.sin(rad), z)), a


def test_bushing_is_shorter_so_it_is_not_clamped():
    bb = pan.make_bushing(p.PAN_BEARING).bounding_box()
    assert bb.size.Z == pytest.approx(p.PAN_BEARING.width - 0.6, abs=0.01)


def test_bearing_lip_has_no_mid_air_ledge(cap):
    # the cap prints upside down, so the lip under the bearing sits on top of an
    # open hole: a 0.6 mm flat step for the bearing, then a 45° slope inward
    b = p.PAN_BEARING
    seat = pan.BEARING_Z0
    assert cap.is_inside(Vector(b.od / 2 - 0.3, 0, seat - 0.1))  # the step the bearing sits on
    assert not cap.is_inside(Vector(b.od / 2 - 1.0, 0, seat - 0.2))  # no wide flat ledge
    assert cap.is_inside(Vector(b.od / 2 - 1.0, 0, seat - 0.8))  # the slope fills in lower down
