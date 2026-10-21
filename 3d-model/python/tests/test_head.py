import pytest
from build123d import Location, Pos, Rot, Cylinder, Vector

import components as c
import head
import params as p
import yoke


def pt(loc, x, y, z):
    """Point given in a component frame, expressed in the head frame"""
    return (loc * Location((x, y, z))).position


@pytest.fixture(scope="module")
def front():
    return head.make_head_front()


@pytest.fixture(scope="module")
def rear():
    return head.make_head_rear()


def test_valid(front, rear):
    assert front.is_valid and rear.is_valid


@pytest.mark.parametrize(
    "keepout,loc",
    [
        ("esp32_keepout", "BOARD_LOC"),
        ("sd_access", "BOARD_LOC"),
        ("usb_plug", "BOARD_LOC"),
        ("hcsr04_keepout", "SR04_LOC"),
        ("laser", "LASER_LOC"),
    ],
)
def test_components_clear_shells(front, rear, keepout, loc):
    k = getattr(c, keepout)().moved(getattr(head, loc))
    assert (k & front).volume < 0.01 and (k & rear).volume < 0.01


def test_front_and_rear_do_not_overlap(front, rear):
    assert (front & rear).volume < 0.5  # contact only


def test_lens_window_open(front):
    x, z = c.board_x(p.LENS_X), c.board_z(p.LENS_Y)
    for dy in (p.LENS_TIP_H + 0.5, p.LENS_TIP_H + 3):
        assert not front.is_inside(pt(head.BOARD_LOC, x, dy, z))


def test_eyes_open(front):
    for sx in (-1, 1):
        tip = pt(head.SR04_LOC, sx * p.SR_TX_DX / 2, p.SR_TX_H + 0.5, 0)
        assert not front.is_inside(tip)


def test_button_pinholes_open(front):
    for bx in p.BTN_XS:
        for dy in (3.0, 6.0):
            assert not front.is_inside(pt(head.BOARD_LOC, bx - p.BOARD_W / 2, dy, p.BOARD_H / 2 - p.BTN_Y))


def test_laser_parallel_to_camera():
    axis = pt(head.LASER_LOC, 0, 1, 0) - pt(head.LASER_LOC, 0, 0, 0)
    assert axis.normalized().Y == pytest.approx(1, abs=1e-6)


def test_laser_held(front):
    # clamp material just outside the tube, beside it
    at = pt(head.LASER_LOC, p.LASER_D / 2 + 1.0, p.LASER_L - 5, 0)
    assert front.is_inside(at)


def test_horn_pocket(front):
    horn = c.mg90s_horn().moved(head.HORN_LOC)
    assert (horn & front).volume < 0.01
    hub = head.HORN_LOC.position
    assert (hub.Y, hub.Z) == pytest.approx((0, 0), abs=1e-6)
    assert hub.X == pytest.approx(-(yoke.ARM_INNER_X - p.MOVE_CLR), abs=1e-6)


def test_fits_between_arms(front, rear):
    collar = Pos(0, 0, 0) * Rot(0, 90, 0) * Cylinder(head.COLLAR_R + 0.01, 200)
    for part in (front, rear):
        bb = (part - collar).bounding_box()
        assert max(abs(bb.min.X), abs(bb.max.X)) <= yoke.ARM_INNER_X - p.MOVE_CLR + 1e-6
        assert part.bounding_box().max.X <= yoke.ARM_INNER_X + 1e-6


def test_axle_socket_and_bolt_hole(front):
    assert not front.is_inside(Vector(yoke.ARM_INNER_X - 2, 0, 0))  # socket for the axle pin
    assert front.is_inside(Vector(yoke.ARM_INNER_X - 2, 0, p.TILT_BEARING.bore / 2 + 1.5))  # its wall
    assert not front.is_inside(Vector(head.AXLE_BOSS_X0 + 1, 0, 0))  # M3 bolt through to the nut inside


def test_collar_touches_inner_ring_only():
    # the 608's inner ring ends about a quarter of the way out from the bore
    b = p.TILT_BEARING
    assert head.COLLAR_R <= b.bore / 2 + (b.od - b.bore) / 4 - 0.3


def test_horn_pocket_inside_head(front):
    bb = c.mg90s_horn(p.FIT).moved(head.HORN_LOC).bounding_box()
    assert bb.min.Z >= head.BOTTOM_OUT + 0.3 and bb.max.Z <= head.TOP_OUT
    assert bb.min.Y >= head.Y_SPLIT + 0.2 and bb.max.Y <= head.Y_FRONT - 0.2


def test_tilt_axle_fits(front):
    axle = head.make_tilt_axle(mounted=True)
    assert axle.is_valid and (axle & front).volume < 0.01
    bb = axle.bounding_box()
    assert bb.max.X == pytest.approx(yoke.ARM_INNER_X + p.TILT_BEARING.width + head.AXLE_FLANGE_T, abs=1e-6)


def test_sd_above_pin_arm():
    sd = c.sd_access().moved(head.BOARD_LOC).bounding_box()
    assert sd.min.Z >= yoke.PIN_ARM_TOP_Z - yoke.TILT_AXIS_Z + p.MOVE_CLR - 1e-6


def test_brows_sit_around_the_cans(front):
    # the cans stand out through the face; the brows are tubes around them,
    # seated in a recess around each eye opening
    brows = head.make_brows(mounted=True)
    sensor = c.hcsr04_keepout().moved(head.SR04_LOC)
    assert (brows & sensor).volume < 0.01
    assert (brows & front).volume < 0.01
    assert head.BROW_R[0] >= p.SR_TX_D / 2 + 0.3
    assert brows.distance_to(front) < 1e-3  # seated on the face, not floating


def test_hcsr04_slides_in_from_the_open_back(front):
    # the sensor goes in from behind before the rear cover: nothing may stand in its way
    sensor = c.hcsr04()
    travel = head.SR_Y - head.Y_SPLIT + 2
    d = 0.0
    while d <= travel:
        moved = sensor.moved(Location((0, -d, 0)) * head.SR04_LOC)
        assert (moved & front).volume < 0.01, f"blocked {d:.0f} mm behind its seat"
        d += 2.0


def test_hcsr04_has_printable_clearance(front):
    x_side = p.SR_W / 2 + p.SR_CLR - 0.1  # just inside the side wall
    for sx in (-1, 1):
        assert not front.is_inside(Vector(sx * x_side, head.SR_Y - 1.0, head.SR_ZC))
    assert not front.is_inside(Vector(0, head.SR_Y - 1.0, head.SR_Z0 + p.SR_H + p.SR_CLR - 0.1))
    assert not front.is_inside(Vector(15, head.SR_Y - 1.0, head.SR_Z0 - p.SR_CLR + 0.1))
    # the outside of the head keeps its width, so the yoke is unchanged
    assert front.bounding_box().max.X <= yoke.ARM_INNER_X + 1e-6


def test_hcsr04_screws_to_corner_posts(front, rear):
    # four solid posts in the corners, part of the walls; an M2 screw from behind
    # through each of the board's corner holes into a pilot hole in the post
    for hx, hz in head.SR_HOLES:
        assert not front.is_inside(Vector(hx, head.SR_Y + 1.0, hz))  # pilot hole
        for dx, dz in ((1.6, 0), (-1.6, 0), (0, 1.6), (0, -1.6)):
            assert front.is_inside(Vector(hx + dx, head.SR_Y + 1.0, hz + dz))  # post around it
    # the thin pegs on the rear cover are gone
    assert rear.bounding_box().max.Y < head.Y_SPLIT + 7


def test_rear_cover_screws_from_the_top(front, rear):
    for x, y in head.TOP_SCREWS:
        assert not front.is_inside(Vector(x, y, head.TOP_OUT - 0.5))  # hole through the top wall
        assert not rear.is_inside(Vector(x, y, head.TOP_IN - 2.0))  # pilot hole in the cover's tab
        assert rear.is_inside(Vector(x + 1.6, y, head.TOP_IN - 2.0))  # the tab around it



def test_camera_opening_is_round_with_led_slots(front):
    # =O= : a round hole the camera block passes through, a slot out to each LED
    y_in_wall = head.Y_FRONT - head.W / 2
    spots = [(p.LENS_X, p.LENS_Y)] + [(x, p.LED_Y) for x in p.LED_XS]
    for fx, fy in spots:
        assert not front.is_inside(pt(head.BOARD_LOC, c.board_x(fx), y_in_wall - head.BOARD_Y, c.board_z(fy))), (fx, fy)
    # the camera block's corners pass through too
    h = p.CAM_MODULE / 2
    for dx in (-h + 0.2, h - 0.2):
        for dz in (-h + 0.2, h - 0.2):
            at = pt(head.BOARD_LOC, c.board_x(p.LENS_X) + dx, y_in_wall - head.BOARD_Y, c.board_z(p.LENS_Y) + dz)
            assert not front.is_inside(at)
    # round, not a rectangle: the face is solid beyond the circle, off the LED slots
    corner = pt(head.BOARD_LOC, c.board_x(p.LENS_X - 5.5), y_in_wall - head.BOARD_Y, c.board_z(p.LENS_Y + 4.5))
    assert front.is_inside(corner)


def test_outside_unchanged_so_the_yoke_still_fits():
    assert head.DEPTH == pytest.approx(38.7)


def test_camera_board_close_to_the_face():
    assert head.FACE_GAP == pytest.approx(4.8)  # PCB front to the inside of the face
    assert head.BOARD_Y + p.LENS_TIP_H >= head.Y_FRONT + 0.5  # the lens pokes out of the face
    assert head.FACE_GAP >= max(p.USB_H, p.SD_SHELL_H) + 0.5  # nothing else touches the face


def test_o_is_as_small_as_the_camera_block_allows():
    assert head.CAM_HOLE_R <= p.CAM_MODULE / 2 * 2**0.5 + 0.3


@pytest.fixture(scope="module")
def plate():
    return head.make_fit_test()


def test_fit_test_is_the_front_of_the_head(plate):
    assert plate.is_valid and len(plate.solids()) == 1
    bb = plate.bounding_box()
    # the face plus a short ring of wall, deep enough to surround both boards
    assert bb.max.Y == pytest.approx(head.Y_FRONT, abs=1e-6)
    assert bb.min.Y == pytest.approx(head.FIT_TEST_Y0, abs=1e-6)
    assert head.FIT_TEST_Y0 <= head.SR_Y - p.PCB_T - 0.5  # behind the HC-SR04's board
    assert head.FIT_TEST_Y0 <= head.BOARD_Y - p.PCB_T - 0.5  # and the camera board's
    y = head.SR_Y - 0.5
    assert plate.is_inside(Vector(head.HEAD_HALF - head.W / 3, y, head.SR_ZC))  # eye section side wall
    assert plate.is_inside(Vector(head.BODY_HALF - 0.5, y, head.BOARD_Z))  # body side wall


def test_fit_test_matches_the_head(front, plate):
    y_in_wall = head.Y_FRONT - head.W / 2
    probes = [pt(head.BOARD_LOC, c.board_x(p.LENS_X), y_in_wall - head.BOARD_Y, c.board_z(p.LENS_Y))]
    probes += [pt(head.SR04_LOC, sx * p.SR_TX_DX / 2, y_in_wall - head.SR_Y, 0) for sx in (-1, 1)]
    probes += [pt(head.BOARD_LOC, c.board_x(x), y_in_wall - head.BOARD_Y, c.board_z(p.BTN_Y)) for x in p.BTN_XS]
    for q in probes:  # openings in the same places
        assert not plate.is_inside(q) and not front.is_inside(q)
    for x, z in head.BOARD_PINS:  # board pins in the same places
        q = Vector(x, head.BOARD_Y - p.PCB_T / 2, z)
        assert plate.is_inside(q) and front.is_inside(q)
    for x, z in head.BOARD_SCREWS:  # and the screw pilot holes
        q = Vector(x, head.BOARD_Y + 1.0, z)
        assert not plate.is_inside(q) and not front.is_inside(q)
    for hx, hz in head.SR_HOLES:  # HC-SR04 corner posts
        q = Vector(hx + 1.6, head.SR_Y + 1.0, hz)
        assert plate.is_inside(q) and front.is_inside(q)



def test_eye_cans_stand_out_of_the_face():
    assert p.CAN_OUT >= 1.0
    assert head.SR_Y + p.SR_TX_H == pytest.approx(head.Y_FRONT + p.CAN_OUT)
    # with the opening wide enough for them
    assert head.EYE_R >= p.SR_TX_D / 2 + 0.3


def test_hcsr04_plugs_clear_the_camera_board():
    plugs = c.hcsr04_keepout().moved(head.SR04_LOC)
    board = c.esp32_board().moved(head.BOARD_LOC)
    assert plugs.distance_to(board) >= 1.0 - 1e-6  # room for parts on the camera board's back


@pytest.mark.parametrize("which", ["status", "flash_left", "flash_right"])
def test_every_led_shows_through_the_face(front, plate, which):
    if which == "status":
        (fx, fy), w = p.STATUS_LED, p.STATUS_LED_W
    else:
        fx, fy, w = p.LED_XS[0 if which == "flash_left" else 1], p.LED_Y, p.LED_W
    # the LED's whole face (its corners) and the full margin beside each edge
    # can see out, from the board through the face (window corners are rounded)
    k, m = w / 2 + 0.3, w / 2 + p.LED_WIN_CLR - 0.2
    spots = [(dx, dz) for dx in (-k, k) for dz in (-k, k)] + [(0, 0), (-m, 0), (m, 0), (0, -m), (0, m)]
    for dx, dz in spots:
        for y in (0.9, head.FACE_GAP / 2, head.FACE_GAP + head.W / 2):
            q = pt(head.BOARD_LOC, c.board_x(fx) + dx, y, c.board_z(fy) + dz)
            assert not front.is_inside(q) and not plate.is_inside(q), (which, dx, dz, y)



def test_sd_slot_has_extra_margin(front):
    import components as comp
    grown = comp.sd_access(p.SD_CLR).moved(head.BOARD_LOC)
    assert (grown & front).volume < 0.01


def test_camera_board_screwed_at_two_corners_pinned_at_two(front):
    # the board can't slide back off its pins: two corners are screwed (M2 from
    # behind, the head clamps the board), the other two keep their locating pins
    for x, z in head.BOARD_SCREWS:
        assert not front.is_inside(Vector(x, head.BOARD_Y + 1.0, z))  # pilot hole in the standoff
        assert front.is_inside(Vector(x + 1.8, head.BOARD_Y + 1.0, z))  # standoff around it
        assert not front.is_inside(Vector(x, head.BOARD_Y - p.PCB_T / 2, z))  # no pin there
    for x, z in head.BOARD_PINS:
        assert front.is_inside(Vector(x, head.BOARD_Y - p.PCB_T / 2, z))  # pin through the hole
    assert len(head.BOARD_SCREWS) == 2 and len(head.BOARD_PINS) == 2
    # diagonal corners, so the pins locate the board in both directions
    (ax, az), (bx, bz) = head.BOARD_PINS
    assert ax == -bx and az != bz


def test_rear_cover_has_a_locating_lip(front, rear):
    # a thin rim that fits just inside the head's opening, so the cover sits
    # right even without its screws
    y = head.Y_SPLIT + head.LIP_DEPTH / 2
    inset = head.LIP_CLR + head.LIP_T / 2
    for q in (Vector(head.EYE_HALF_IN - inset, y, head.SR_ZC),       # eye section side
              Vector(-(head.EYE_HALF_IN - inset), y, head.SR_ZC),
              Vector(head.BODY_HALF - head.W - inset, y, head.BOARD_Z),  # body side
              Vector(0, y, head.TOP_IN - inset)):                       # top
        assert rear.is_inside(q), q
    assert (front & rear).volume < 0.5  # it doesn't press into the walls
