import pytest
from build123d import Vector

import base
import components as c
import params as p


@pytest.fixture(scope="module")
def b():
    return base.make_base()


def test_valid_single_solid(b):
    assert b.is_valid and len(b.solids()) == 1


def test_footprint(b):
    bb = b.bounding_box()
    assert bb.min.Z == pytest.approx(0, abs=1e-6)
    # the drum may overhang the plate, but never beyond its own radius
    r_out = base.drum_radii()[1]
    assert bb.size.X <= 2 * r_out + 0.01 and bb.size.Y <= 2 * r_out + 0.01


def test_plate_outline_at_z1(b):
    # long side along Y by default; at z=1 only the plate exists
    assert b.is_inside(Vector(p.BASE_W / 2 - 0.5, 0, 1))
    assert not b.is_inside(Vector(p.BASE_W / 2 + 0.5, 0, 1))
    assert b.is_inside(Vector(6, -(p.BASE_L / 2 - 0.5), 1))  # beside the servo-cable hole
    assert not b.is_inside(Vector(0, p.BASE_L / 2 + 0.5, 1))


@pytest.mark.parametrize("sx", [-1, 1])
@pytest.mark.parametrize("sy", [-1, 1])
def test_screw_holes_and_counterbores(b, sx, sy):
    x, y = sx * p.BASE_HOLE_DX / 2, sy * p.BASE_HOLE_DY / 2
    assert not b.is_inside(Vector(x + 1.0, y, 1.0))  # Ø2.2 through hole
    assert b.is_inside(Vector(x + 1.4, y, 1.0))  # plate around it
    assert not b.is_inside(Vector(x + 2.0, y, p.BASE_BOSS_H - 1.0))  # Ø4.4 counterbore
    for z in (p.BASE_BOSS_H + 2, base.NECK_TOP_Z):  # screwdriver access from above
        assert not b.is_inside(Vector(x, y, z))


def test_long_axis_switch():
    bx = base.make_base("X")
    assert bx.is_valid
    assert bx.is_inside(Vector(p.BASE_L / 2 - 0.5, 6, 1))
    assert not bx.is_inside(Vector(0, p.BASE_W / 2 + 0.5, 1))
    servo = c.mg90s().moved(base.pan_servo_loc("X"))
    assert (servo & bx).volume < 0.01


def test_pan_servo_fits(b):
    servo = c.mg90s().moved(base.PAN_SERVO_LOC)
    assert (servo & b).volume < 0.01


def test_pan_servo_shaft_on_axis():
    shaft = base.PAN_SERVO_LOC.position
    assert (shaft.X, shaft.Y) == pytest.approx((0, 0), abs=1e-6)


def test_cable_hole_fits_bundle(b):
    w, d = base.CABLE_HOLE
    assert w * d >= (p.WIRE_COUNT + 3) * p.WIRE_D**2 * 1.5  # the head's bundle plus the pan servo's cable
    x, y = base.CABLE_HOLE_XY
    assert not b.is_inside(Vector(x, y, 1.0))


def test_pan_servo_cable_runs_under_the_front_pillar(b):
    # the MG90S cable leaves the shaft end of the body, at the bottom; it runs
    # forward under the arch of the front pillar to the plate's cable hole
    end_y = c.servo_body_x() + p.SERVO_L / 2  # shaft end face (servo x -> world y)
    hole_y0 = base.CABLE_HOLE_XY[1] - base.CABLE_HOLE[1] / 2
    path = c.box(-p.PLUG_W / 2, p.PLUG_W / 2, end_y, hole_y0 + 1, p.BASE_PLATE_T, p.BASE_PLATE_T + p.PLUG_T)
    assert (path & b).volume < 0.01
    assert not b.is_inside(Vector(0, hole_y0 + 1, 1.0))  # and down through the plate


def test_front_tab_screw_still_has_plastic(b):
    # the tab screw goes into the arch's roof, above the cable
    y = c.servo_body_x() + p.SERVO_TAB_HOLE_PITCH / 2
    z = base.TAB_Z0 - 5
    assert b.is_inside(Vector(1.2, y, z))  # beside the pilot hole
    assert not b.is_inside(Vector(0, y, z))  # the pilot hole