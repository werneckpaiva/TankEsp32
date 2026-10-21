import pytest
import params as p


def test_base_pattern_matches_reference():
    assert (p.BASE_L, p.BASE_W) == (41.8, 30.8)
    assert (p.BASE_HOLE_DX, p.BASE_HOLE_DY, p.BASE_HOLE_D) == (22.0, 33.0, 2.2)
    assert (p.BASE_CBORE_D, p.BASE_CBORE_DEPTH) == (4.4, 2.2)


def test_bearing_defaults():
    assert p.PAN_BEARING == p.Bearing(8, 22, 7)
    assert p.TILT_BEARING == p.Bearing(8, 22, 7)  # the user's 608s, both axes


def test_ranges():
    assert p.PAN_RANGE == (-90, 90) and p.TILT_RANGE == (-45, 90)


def test_board_features_on_board():
    for x in (p.LENS_X, *p.LED_XS, p.SD_X0, *p.BTN_XS):
        assert 0 <= x <= p.BOARD_W
    # measured on the user's board (upright, USB-C down, camera facing you)
    assert p.LENS_Y == pytest.approx(13 - 7.94 / 2)
    assert p.LENS_X == pytest.approx(p.BOARD_W - (19 - 7.94 / 2))
    assert p.LED_XS == pytest.approx((9.0, p.BOARD_W - 7.0))


def test_measured_board_heights():
    # measured on the user's board, above the PCB's front face (totals minus the 1.6 mm PCB)
    assert p.LENS_TIP_H == pytest.approx(8.65 - 1.6)
    assert p.USB_H == pytest.approx(4.85 - 1.6)
    assert p.SD_SHELL_H == pytest.approx(4.8 - 1.6)
    assert p.SR_HOLE_D == pytest.approx(2.0)
