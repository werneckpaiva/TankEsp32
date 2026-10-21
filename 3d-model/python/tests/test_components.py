import pytest
from build123d import Vector

import components as c
import params as p


def size(part):
    bb = part.bounding_box()
    return (bb.size.X, bb.size.Y, bb.size.Z)


def test_board_pcb_outline():
    sx, _, sz = size(c.esp32_board())
    assert sx == pytest.approx(p.BOARD_W, abs=0.01)
    assert sz == pytest.approx(p.BOARD_H + p.USB_OVERHANG, abs=0.01)


def test_board_lens_position():
    # lens on the +Y side, at LENS_X from the left edge (seen from the front), LENS_Y below the top
    probe = Vector(c.board_x(p.LENS_X), p.CAM_BLOCK_H + 0.5, c.board_z(p.LENS_Y))
    assert c.esp32_board().is_inside(probe)  # the lens barrel in front of the camera block
    assert not c.esp32_board().is_inside(Vector(c.board_x(p.LENS_X), p.LENS_TIP_H + 0.2, c.board_z(p.LENS_Y)))


def test_board_sd_on_plus_x_side():
    # seen from the front the SD socket is top-left, which is +X (the head's right from behind)
    sd_x = p.BOARD_W / 2 - (p.SD_X0 + p.SD_SHELL_W / 2)
    probe = Vector(sd_x, p.PCB_T / 2 + p.SD_SHELL_H / 2, p.BOARD_H / 2 - p.SD_Y0 - p.SD_SHELL_L / 2)
    assert sd_x > 0 and c.esp32_board().is_inside(probe)


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


def test_horn_hub_on_axis():
    h = c.mg90s_horn()
    assert h.bounding_box().min.Z == pytest.approx(0, abs=1e-6)
    assert h.bounding_box().size.X == pytest.approx(2 * p.HORN_ARM_L + p.HORN_ARM_W_TIP, abs=0.5)


def test_bearing_envelope():
    b = c.bearing(p.PAN_BEARING)
    assert size(b) == pytest.approx((22, 22, 7), abs=0.01)
    assert not b.is_inside(Vector(0, 0, 0))


def test_board_has_the_status_led():
    fx, fy = p.STATUS_LED
    assert (fx, fy) == pytest.approx((6.0, 3.0))  # right side 7 mm from the left edge, bottom edge 4 mm from the top
    assert c.esp32_board().is_inside(Vector(c.board_x(fx), 0.4, c.board_z(fy)))


def test_keepout_leaves_room_beside_the_header_plugs():
    # Dupont plugs sit on the header rows at the board's sides; their wires need room beside them
    ko = c.esp32_keepout().bounding_box()
    assert ko.max.X >= p.BOARD_W / 2 - p.HDR_X_INSET + p.DUPONT_W / 2 + 1.0 - 1e-6
