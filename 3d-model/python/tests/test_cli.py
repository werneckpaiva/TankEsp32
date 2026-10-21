import pytest

import gimbal_head as g


def test_defaults_to_rest_pose():
    args = g.parse_args([])
    assert (args.pan, args.tilt) == (0, 0)


def test_takes_pan_and_tilt():
    args = g.parse_args(["--pan", "45", "--tilt", "-30"])
    assert (args.pan, args.tilt) == (45, -30)


@pytest.mark.parametrize("argv", [["--pan", "91"], ["--pan", "-120"], ["--tilt", "-46"], ["--tilt", "95"]])
def test_rejects_angles_outside_the_range(argv):
    with pytest.raises(SystemExit):
        g.parse_args(argv)
