import importlib

import pytest

import gimbal_head as g
import params as p


def group(parts, names):
    out = None
    for n in sorted(names):
        out = parts[n] if out is None else out + parts[n]
    return out


TILTS = list(range(p.TILT_RANGE[0], p.TILT_RANGE[1] + 1, 15)) + [p.TILT_RANGE[1]]


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
    moving = group(parts, (g.PANNING | g.TILTING) - {"pan_coupler"})
    assert moving.distance_to(parts["base"]) >= p.MOVE_CLR - 1e-3


def test_positive_pan_turns_toward_plus_x():
    loc = g.head_to_world(30, 0)
    ahead = (loc * g.Location((0, 1, 0))).position - loc.position
    assert ahead.X > 0.4


def test_positive_tilt_looks_up():
    loc = g.head_to_world(0, 30)
    ahead = (loc * g.Location((0, 1, 0))).position - loc.position
    assert ahead.Z > 0.4


def test_usb_plug_reachable_at_tilt_up():
    import components as c
    import head

    parts = g.place(0, p.TILT_RANGE[1])
    plug = c.usb_plug().moved(g.head_to_world(0, p.TILT_RANGE[1]) * head.BOARD_LOC)
    others = group(parts, g.PANNING | g.STATIC)
    assert (plug & others).volume < 0.01


def test_sd_card_reachable_at_rest():
    import components as c
    import head

    parts = g.place(0, 0)
    ko = c.sd_access().moved(g.head_to_world(0, 0) * head.BOARD_LOC)
    assert (ko & parts["yoke"]).volume < 0.01


@pytest.mark.parametrize(
    "name,delta", [("SERVO_W", 0.4), ("HORN_HUB_D", 0.4), ("SR_TX_D", 0.5), ("LASER_D", 0.3), ("BAY_DEPTH", 6.0)]
)
def test_rebuilds_with_perturbed_params(name, delta):
    import base
    import components
    import head
    import pan
    import params
    import yoke

    mods = (params, components, base, pan, head, yoke, g)  # dependency order: yoke reads the head
    try:
        importlib.reload(params)
        setattr(params, name, getattr(params, name) + delta)
        for m in mods[1:]:
            importlib.reload(m)
        parts = g.place(0, 0)
        assert all(part.is_valid for part in parts.values())
        for tilt in (p.TILT_RANGE[0], 0, p.TILT_RANGE[1]):
            parts = g.place(0, tilt)
            assert (group(parts, g.TILTING) & group(parts, g.PANNING | g.STATIC)).volume < 0.01, tilt
    finally:
        for m in mods:
            importlib.reload(m)


def test_head_wire_exit_above_yoke_hole():
    import math
    import base
    import head
    r = sum(base.wire_slot()) / 2
    a = math.radians(p.WIRE_ANGLE)
    assert (head.WIRE_EXIT_X, 0) == pytest.approx((r * math.cos(a), r * math.sin(a)), abs=1e-6)


@pytest.mark.parametrize("tilt", TILTS)
def test_wire_corridor_never_pinched(tilt):
    """Where the bundle runs from the head's exit into the yoke's hole, the head
    never comes closer than 3.5 mm to the yoke"""
    import head
    import yoke
    parts = g.place(0, tilt)
    corridor = g.Pos(head.WIRE_EXIT_X, 0, 0) * g.Box(6, 14, 400)
    near_head = (parts["head_front"] + parts["head_rear"]) & corridor
    near_yoke = parts["yoke"] & corridor
    if near_head.volume > 0:
        assert near_head.distance_to(near_yoke) >= 3.5, f"tilt {tilt}°"


def test_tilt_axle_runs_in_the_bearing():
    parts = g.place(0, 0)
    for other in ("tilt_bearing", "yoke", "pin_arm"):
        assert (parts["tilt_axle"] & parts[other]).volume < 0.01, other
