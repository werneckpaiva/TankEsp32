"""
Head: a front shell carrying everything, and a rear cover closing the back.

Head frame: origin on the tilt axis midway between the yoke arms, +Y forward
(camera direction at tilt 0), +Z up, +X toward the SD card side.

Layout, front view:
    top        laser clamp
    eyes       HC-SR04 behind the face, slid in from the back and screwed (4 x M2,
               through its corner holes) to four corner posts; its cans stand
               out through the face, inside two brow tubes. Wider than the rest
               of the head.
    body       ESP32-S3-CAM upright on four standoff pins, camera through the
               face, USB-C opening underneath, BOOT/RESET pinholes, SD slot in
               the +X side wall.
    sides      -X: horn pocket for the tilt servo. +X: M3 axle into the head,
               through the bearing in the yoke's slim arm.
    back       Dupont bay behind the board; the HC-SR04's plugs hang down into
               it behind the board; the wires leave through the bottom,
               under the tilt axis and straight above the yoke's wire hole.
    brows      two separate tubes seated in recesses around the eye openings,
               so the face prints flat on the bed.
"""

from functools import cache
from math import cos, radians, sin

from build123d import *

import base
import components as c
import params as p

HEAD_HALF = p.SR_W / 2 + p.FIT + p.HEAD_WALL  # widest point (the eye section); the yoke arms stand outside it
ARM_X = HEAD_HALF + p.MOVE_CLR  # inner faces of the yoke arms
BODY_HALF = p.BOARD_W / 2 + p.FIT + 3.0 * MM + p.HEAD_WALL  # around the board, room for cover-screw posts
W = p.HEAD_WALL

# Depth: the face sits FACE_GAP in front of the board (taller parts, the camera,
# pass through the visor), the Dupont bay behind it
FACE_GAP = 4.8 * MM  # the lens pokes out of the face; USB-C and SD clear it by 1.5 mm
DEPTH = FACE_GAP + W + p.BAY_DEPTH + W
Y_FRONT = DEPTH / 2  # pivot halfway through the depth
Y_BACK = -DEPTH / 2
Y_SPLIT = Y_BACK + W  # rear cover = back wall
BOARD_Y = Y_FRONT - W - FACE_GAP  # PCB front face

# Height: the SD card (top corner of the board) must sit above the slim arm
SD_ZC = p.BOARD_H / 2 - p.SD_Y0 - p.SD_SHELL_L / 2  # in the board frame
SD_HALF_H = p.SD_CARD_W / 2 + 1 * MM  # fingertip box half height
BOARD_Z = p.PIN_ARM_REACH + p.MOVE_CLR + SD_HALF_H - SD_ZC
SR_Z0 = BOARD_Z + p.BOARD_H / 2 + 1.0 * MM  # HC-SR04 PCB bottom edge
SR_ZC = SR_Z0 + p.SR_H / 2
SR_Y = Y_FRONT + p.CAN_OUT - p.SR_TX_H  # PCB front face, set by front ribs; the cans stand out of the face
EYE_FLOOR = SR_Z0 - p.SR_CLR  # inside
TOP_IN = SR_Z0 + p.SR_H + p.SR_CLR
EYE_HALF_IN = p.SR_W / 2 + p.SR_CLR  # inside half-width of the eye section (its side walls are a bit thinner)
TOP_OUT = TOP_IN + W
BOTTOM_IN = BOARD_Z - p.BOARD_H / 2 - p.USB_OVERHANG - p.FIT
BOTTOM_OUT = BOTTOM_IN - W
EYE_OUT_BOTTOM = EYE_FLOOR - W

# Laser: on top, centred, front end flush with the face
LASER_Z = TOP_OUT + 2.0 * MM + p.LASER_D / 2
LASER_CLAMP_L = 18.0 * MM

BOARD_LOC = Location((0, BOARD_Y, BOARD_Z))
SR04_LOC = Location((0, SR_Y, SR_ZC))
LASER_LOC = Location((0, Y_FRONT - p.LASER_L, LASER_Z))
HORN_ANGLE = 22  # horn arms tilted in the YZ plane so they fit inside the head's depth and height
HORN_LOC = Location(
    Plane(origin=(-HEAD_HALF, 0, 0), x_dir=(0, cos(radians(HORN_ANGLE)), sin(radians(HORN_ANGLE))), z_dir=(1, 0, 0))
)

# Wires leave through the bottom, straight above the yoke's wire hole
WIRE_EXIT_X = sum(base.wire_slot()) / 2 * cos(radians(p.WIRE_ANGLE))
WIRE_EXIT = (5.5 * MM, 13.0 * MM)  # x, y size of the exit: the bundle at WIRE_FILL, or a servo plug

# Rear cover screws into posts in the front shell: (x, z) pairs
# (posts at the top would block the HC-SR04's way in from the back, so the top
# of the cover is screwed from above, through the head's top wall into tabs on the cover)
COVER_SCREWS = [(sx * (BODY_HALF - W - 1.6 * MM), BOTTOM_IN + 2.5 * MM) for sx in (-1, 1)]
TOP_SCREWS = [(sx * 10 * MM, Y_SPLIT + 3.0 * MM) for sx in (-1, 1)]  # (x, y), M2 from above
# Camera board: pinned at two diagonal corners (they locate it), screwed at the
# other two (M2 from behind; the screw heads clamp the board so it can't slide back)
_BOARD_HOLES = {(hx, hz): (hx * (p.BOARD_W / 2 - p.BOARD_HOLE_INSET), BOARD_Z + hz * (p.BOARD_H / 2 - p.BOARD_HOLE_INSET))
                for hx in (-1, 1) for hz in (-1, 1)}
BOARD_PINS = [_BOARD_HOLES[(1, 1)], _BOARD_HOLES[(-1, -1)]]  # +X top is beside the status LED: a pin, not a screw
BOARD_SCREWS = [_BOARD_HOLES[(-1, 1)], _BOARD_HOLES[(1, -1)]]
SR_HOLES = [(x, SR_ZC + z) for x, z in c.sr_holes()]  # HC-SR04 mounting holes (x, z), screwed to corner posts
SR_POST_R = p.M2_PILOT / 2 + 1.2 * MM  # material round each post's pilot hole
CAM_HOLE_R = p.CAM_MODULE / 2 * 2**0.5 + 0.25 * MM  # the O: just clears the square camera block's corners


ROUND = 2.5 * MM  # outer edge rounding; more would thin the walls at the corners
assert p.TILT_BEARING.bore >= 6 * MM, "the tilt axle is a printed pin: use a bearing with a bore of 6 mm or more"
COLLAR_R = p.TILT_BEARING.bore / 2 + (p.TILT_BEARING.od - p.TILT_BEARING.bore) / 8  # bears on the inner ring only
AXLE_SOCKET_DEPTH = 5.0 * MM  # how far the axle pin goes into the head
AXLE_FLANGE_T = 1.5 * MM  # pin flange outside the bearing, under the bolt head
AXLE_BOSS_X0 = BODY_HALF - W  # the axle boss starts at the wall (clear of the header plugs); the nut sits on its end
EYE_R = p.SR_TX_D / 2 + 0.4 * MM  # eye opening; the transducer cans pass through it
BROW_R = (p.SR_TX_D / 2 + 0.5 * MM, p.SR_TX_D / 2 + 2.9 * MM)  # brow tube inner/outer radius, around the can
BROW_H = 4.0 * MM  # how far the brows stand off the face
SPIGOT = (1.0 * MM, 0.8 * MM)  # brow spigot: radial width, depth into the recess around the eye opening
BROW_SEAT_R = BROW_R[0] + SPIGOT[0] + 0.2 * MM  # recess in the face the spigot sits in


def rounded_box(x: float, y: float, z0: float, z1: float, r: float) -> Part:
    """Box with its edges along Y rounded and the front and back outlines
    chamfered at 45° (the front lies on the bed when printing)"""
    b = Pos(0, 0, (z0 + z1) / 2) * Box(2 * x, y[1] - y[0], z1 - z0)
    b = Pos(0, (y[0] + y[1]) / 2, 0) * b
    b = fillet(b.edges().filter_by(Axis.Y), r)
    return chamfer(b.faces().sort_by(Axis.Y)[0].edges() + b.faces().sort_by(Axis.Y)[-1].edges(), r * 0.6)


def cyl_y(r: float, y0: float, y1: float, x: float, z: float) -> Part:
    return c.cyl_y(r, y0, y1, x, z)


def outer_shell() -> Part:
    ys = (Y_BACK, Y_FRONT)
    eyes = rounded_box(HEAD_HALF, ys, EYE_OUT_BOTTOM, TOP_OUT, ROUND)
    body = rounded_box(BODY_HALF, ys, BOTTOM_OUT, EYE_OUT_BOTTOM + 5 * MM, ROUND)
    # 45° shoulders from the body up to the eye section (print without support)
    drop = HEAD_HALF - BODY_HALF
    with BuildSketch(Plane.XZ) as shoulder:
        Polygon((-BODY_HALF, EYE_OUT_BOTTOM - drop), (BODY_HALF, EYE_OUT_BOTTOM - drop),
                (HEAD_HALF, EYE_OUT_BOTTOM + 1), (-HEAD_HALF, EYE_OUT_BOTTOM + 1), align=None)
    shoulders = Pos(0, Y_FRONT - 2, 0) * extrude(shoulder.sketch, DEPTH - 4)
    return eyes + body + shoulders


def cavity() -> Part:
    ys = (Y_BACK + W, Y_FRONT - W)
    # square inside corners: the HC-SR04 fills the eye section edge to edge
    eyes = c.box(-EYE_HALF_IN, EYE_HALF_IN, *ys, EYE_FLOOR, TOP_IN)
    body = c.box(-BODY_HALF + W, BODY_HALF - W, *ys, BOTTOM_IN, EYE_FLOOR + 3)
    return eyes + body


def face_mounts() -> Part:
    """What stands off the inside of the face: the camera board's standoffs and
    pins, and the corner posts the HC-SR04's board rests on and screws to"""
    mounts = []
    for x, z in _BOARD_HOLES.values():
        mounts.append(cyl_y(2.2 * MM, BOARD_Y, Y_FRONT - W + 0.5, x, z))  # standoff
    for x, z in BOARD_PINS:
        mounts.append(cyl_y((p.BOARD_HOLE_D - 0.1) / 2, BOARD_Y - p.PCB_T, BOARD_Y, x, z))  # snug locating pin
    # HC-SR04 corner posts, filling each corner of the eye section into the side
    # wall and the ceiling or floor; the board rests on them and screws to them
    for hx, hz in SR_HOLES:
        x_wall = (1 if hx > 0 else -1) * (EYE_HALF_IN + 0.5)
        z_wall = TOP_IN + 0.5 if hz > SR_ZC else EYE_FLOOR - 0.5
        x0, x1 = sorted((hx - (1 if hx > 0 else -1) * SR_POST_R, x_wall))
        z0, z1 = sorted((hz - (1 if hz > SR_ZC else -1) * SR_POST_R, z_wall))
        mounts.append(c.box(x0, x1, SR_Y, Y_FRONT - W + 0.5, z0, z1))
    return mounts[0] + mounts[1:]


def face_openings() -> Part:
    """Everything cut through the face: the two eye openings, the =O= opening
    (a round hole the square camera block passes through, as it stands taller
    than the face's gap, and a slot out to each flash LED), the status LED's
    window, the button pinholes and the pilot holes for the HC-SR04's screws"""
    cuts = []
    for sx in (-1, 1):
        cuts.append(cyl_y(EYE_R, Y_FRONT - W - 1, Y_FRONT + 1, sx * p.SR_TX_DX / 2, SR_ZC))  # the can passes through
        cuts.append(cyl_y(BROW_SEAT_R, Y_FRONT - SPIGOT[1], Y_FRONT + 1, sx * p.SR_TX_DX / 2, SR_ZC))  # brow seat
    lens_x, lens_z = c.board_x(p.LENS_X), BOARD_Z + c.board_z(p.LENS_Y)
    hole_r = CAM_HOLE_R
    slot_h = p.LED_W + 2 * p.LED_WIN_CLR
    led_z = BOARD_Z + c.board_z(p.LED_Y)
    with BuildSketch(Plane.XZ.offset(-(Y_FRONT + 1))) as opening:
        with Locations((lens_x, lens_z)):
            Circle(hole_r)
        for fx in p.LED_XS:
            x_out = c.board_x(fx) + (1 if c.board_x(fx) > lens_x else -1) * (p.LED_W / 2 + p.LED_WIN_CLR - slot_h / 2)
            with Locations(((x_out + lens_x) / 2, led_z)):
                SlotCenterToCenter(abs(x_out - lens_x), slot_h)
    cuts.append(extrude(opening.sketch, W + 2.5))
    # status LED, in the top-left corner beside a mounting hole: a window, and
    # the same opening through the standoff in front of it so its light gets out
    sx, sy = p.STATUS_LED
    half = p.STATUS_LED_W / 2 + p.LED_WIN_CLR
    with BuildSketch(Plane.XZ.offset(-(Y_FRONT + 1))) as status:
        with Locations((c.board_x(sx), BOARD_Z + c.board_z(sy))):
            RectangleRounded(2 * half, 2 * half, 0.8 * MM)
    cuts.append(extrude(status.sketch, Y_FRONT + 1 - BOARD_Y))
    for x in p.BTN_XS:
        cuts.append(cyl_y(p.PINHOLE_D / 2, BOARD_Y, Y_FRONT + 1, c.board_x(x), BOARD_Z + c.board_z(p.BTN_Y)))
    for x, z in BOARD_SCREWS:  # pilot holes for the camera board's M2 screws
        cuts.append(cyl_y(p.M2_PILOT / 2, BOARD_Y - 1, BOARD_Y + 5 * MM, x, z))
    for hx, hz in SR_HOLES:  # pilot holes for the HC-SR04's M2 screws
        cuts.append(cyl_y(p.M2_PILOT / 2, SR_Y - 1, SR_Y + 7 * MM, hx, hz))
    return cuts[0] + cuts[1:]


def make_shell() -> Part:
    shell = outer_shell() - cavity()
    shell += face_mounts()
    shell -= face_openings()  # (the brow rings plug into the eye openings from outside)

    # -X: bar holding the horn pocket
    bar_h = p.HORN_HUB_D + 2 * p.FIT + 2 * 1.6 * MM + 2
    front_end = (p.HORN_ARM_L * cos(radians(HORN_ANGLE)), p.HORN_ARM_L * sin(radians(HORN_ANGLE)))
    with BuildSketch(Plane.YZ.offset(-HEAD_HALF)) as bar:
        SlotCenterToCenter(2 * p.HORN_ARM_L, bar_h, rotation=HORN_ANGLE)
        # run the front end square to the face, which is on the bed when printing
        with Locations(((front_end[0] + Y_FRONT) / 2, front_end[1])):
            Rectangle(Y_FRONT - front_end[0], bar_h)
    bar_part = extrude(bar.sketch, HEAD_HALF - BODY_HALF + W)
    shell += bar_part & c.box(-HEAD_HALF, 0, Y_SPLIT, Y_FRONT, BOTTOM_OUT, TOP_OUT)
    shell -= c.mg90s_horn(p.FIT).moved(HORN_LOC)  # the hub face is flush with the side, so it opens outward

    # +X: boss with a socket for the axle pin, a collar bearing on the tilt
    # bearing's inner ring, and a hole for the M3 bolt (nut inside the head)
    r_boss = p.TILT_BEARING.bore / 2 + 3 * MM
    # teardrop pointing at the face, so its underside prints without support
    tip = r_boss / sin(radians(40))
    with BuildSketch(Plane.YZ.offset(AXLE_BOSS_X0)) as drop:
        Circle(r_boss)
        Polygon((tip, 0), (r_boss * cos(radians(50)), r_boss * sin(radians(50))),
                (r_boss * cos(radians(50)), -r_boss * sin(radians(50))), align=None)
    shell += extrude(drop.sketch, HEAD_HALF - AXLE_BOSS_X0)
    shell += Pos(HEAD_HALF, 0, 0) * Rot(0, 90, 0) * Cylinder(COLLAR_R, p.MOVE_CLR, align=c.MIN)
    sock_x0 = HEAD_HALF - AXLE_SOCKET_DEPTH - 0.3 * MM  # pin length counts the collar; 0.3 mm left at the bottom
    shell -= Pos(sock_x0, 0, 0) * Rot(0, 90, 0) * Cylinder(p.TILT_BEARING.bore / 2 + 0.05, ARM_X - sock_x0 + 1, align=c.MIN)
    shell -= Pos(AXLE_BOSS_X0 - 1, 0, 0) * Rot(0, 90, 0) * Cylinder(p.M3_CLEAR / 2, ARM_X - AXLE_BOSS_X0 + 1, align=c.MIN)

    # Underside: USB-C plug opening and the wire exit at the back
    usb_y = BOARD_Y + p.USB_H / 2
    shell -= Pos(0, usb_y, BOTTOM_OUT - 1) * Box(p.USB_PLUG_W + 0.5, p.USB_PLUG_T + 0.5, W + 3, align=c.MIN)
    shell -= Pos(WIRE_EXIT_X, 0, BOTTOM_OUT - 1) * Box(*WIRE_EXIT, W + 3, align=c.MIN)

    # SD card slot through the +X side, with room for a fingertip
    shell -= c.sd_access(p.SD_CLR).moved(BOARD_LOC)

    # Laser clamp: split ring on top, pinched by an M2 screw across the split
    r_in, r_out = p.LASER_D / 2 + p.FIT / 2, p.LASER_D / 2 + 2.2 * MM
    y0 = Y_FRONT - LASER_CLAMP_L
    clamp = cyl_y(r_out, y0, Y_FRONT, 0, LASER_Z)
    clamp += c.box(-r_out, r_out, y0, Y_FRONT, TOP_OUT - 1, LASER_Z)  # foot
    ear_z = LASER_Z + r_in + 2.5 * MM
    clamp += c.box(-4.5 * MM, 4.5 * MM, y0, Y_FRONT, LASER_Z, ear_z + 2.5 * MM)  # full length: nothing overhangs face down
    clamp -= cyl_y(r_in, y0 - 1, Y_FRONT + 1, 0, LASER_Z)
    clamp -= c.box(-0.7 * MM, 0.7 * MM, y0 - 1, Y_FRONT + 1, LASER_Z, ear_z + 5)  # the split
    clamp -= Pos(-6, y0 + 4.5 * MM, ear_z) * Rot(0, 90, 0) * Cylinder(p.M2_CLEAR / 2, 6, align=c.MIN)
    clamp -= Pos(0, y0 + 4.5 * MM, ear_z) * Rot(0, 90, 0) * Cylinder(p.M2_PILOT / 2, 6, align=c.MIN)
    shell += clamp
    # laser wires into the head behind the clamp
    shell -= Pos(0, Y_FRONT - p.LASER_L + 3, TOP_IN - 1) * Cylinder(2.5 * MM, W + 3, align=c.MIN)

    # Holes for the screws holding the top of the rear cover
    for x, y in TOP_SCREWS:
        shell -= Pos(x, y, TOP_IN - 1) * Cylinder(p.M2_CLEAR / 2, W + 2, align=c.MIN)

    # Posts for the rear cover screws
    for x, z in COVER_SCREWS:
        # each post runs into the nearest wall (ceiling or floor) so it is printed attached
        z0 = BOTTOM_IN - 0.5 if z < 0 else z - 2.4
        z1 = TOP_IN + 0.5 if z > 0 else z + 2.4
        post = c.box(x - 1.6, x + 1.6, Y_SPLIT, Y_SPLIT + 8, z0, z1)
        # taper the front end into its wall (it hangs face down when printing)
        h, wall_z = z1 - z0, (z1 if z > 0 else z0)
        far_z = z0 if z > 0 else z1
        with BuildSketch(Plane.YZ.offset(x - 1.6)) as wedge:
            Polygon((Y_SPLIT + 8, wall_z), (Y_SPLIT + 8, far_z), (Y_SPLIT + 8 + 1.25 * h, wall_z), align=None)
        post += extrude(wedge.sketch, 3.2)
        shell += post - cyl_y(p.M2_PILOT / 2, Y_SPLIT - 1, Y_SPLIT + 8, x, z)
    return shell


def make_head_front() -> Part:
    return make_shell() & c.box(-100, 100, Y_SPLIT, 100, -100, 100)


# Locating lip on the rear cover: a thin rim just inside the head's opening
LIP_T = 1.2 * MM
LIP_DEPTH = 3.0 * MM
LIP_CLR = 0.2 * MM  # gap to the head's inside walls
LIP_Z0 = BOTTOM_IN + 4.9 * MM + 0.5 * MM  # the lip stops above the bottom screw posts and the board's wire bay


def cavity_outline(inset: float) -> Part:
    """The head's inside outline (eye section over the body), shrunk by inset,
    as a slab where the rear cover meets the head"""
    y0, y1 = Y_SPLIT - 0.01, Y_SPLIT + LIP_DEPTH
    eyes = c.box(-EYE_HALF_IN + inset, EYE_HALF_IN - inset, y0, y1, EYE_FLOOR + inset, TOP_IN - inset)
    body = c.box(-(BODY_HALF - W) + inset, BODY_HALF - W - inset, y0, y1, BOTTOM_IN + inset, EYE_FLOOR + 3)
    return eyes + body


def make_head_rear() -> Part:
    plate = make_shell() & c.box(-100, 100, -100, Y_SPLIT, -100, 100)
    # locating lip along the top and both sides, so the cover sits right even without screws
    lip = cavity_outline(LIP_CLR) - cavity_outline(LIP_CLR + LIP_T)
    plate += lip & c.box(-100, 100, -100, 100, LIP_Z0, 100)
    # tabs under the top wall, taking the top screws
    for x, y in TOP_SCREWS:
        plate += c.box(x - 2.5, x + 2.5, Y_SPLIT - 0.5, y + 3.0, TOP_IN - 4.0, TOP_IN - 0.05)
        plate -= Pos(x, y, TOP_IN - 4.5) * Cylinder(p.M2_PILOT / 2, 5, align=c.MIN)
    for x, z in COVER_SCREWS:
        plate -= cyl_y(p.M2_CLEAR / 2, Y_BACK - 1, Y_SPLIT + 1, x, z)
    return plate


def make_brows(mounted: bool = False) -> Part:
    """The two brow rings. Flat on the bed (tube end down, spigot up) for
    printing, or mounted on the face for the assembly view"""
    # a tube around the can that stands out of the face, and a short spigot
    # that sits in the recess around the eye opening
    ring = Cylinder(BROW_R[1], BROW_H, align=c.MIN) - Cylinder(BROW_R[0], BROW_H, align=c.MIN)
    spigot_r = BROW_R[0] + SPIGOT[0]
    ring += Pos(0, 0, BROW_H) * (Cylinder(spigot_r, SPIGOT[1], align=c.MIN) - Cylinder(BROW_R[0], SPIGOT[1], align=c.MIN))
    if not mounted:
        gap = 2 * BROW_R[1] + 3
        return Pos(-gap / 2, 0, 0) * ring + Pos(gap / 2, 0, 0) * ring
    # tube end forward, spigot into the recess around the eye opening
    on_face = Rot(90, 0, 0) * ring  # local +Z -> -Y
    return Compound(
        [Pos(sx * p.SR_TX_DX / 2, Y_FRONT + BROW_H, SR_ZC) * on_face for sx in (-1, 1)]
    )


@cache
def drop_below_axis() -> float:
    """How far below the tilt axis the head reaches anywhere in its tilt range"""
    shells = make_head_front() + make_head_rear()
    lowest = 0.0
    lo, hi = p.TILT_RANGE
    for k in range(int((hi - lo) / 2.5) + 1):
        tilt = lo + 2.5 * k
        lowest = min(lowest, (Rot(tilt, 0, 0) * shells).bounding_box().min.Z)
    return -lowest



def make_tilt_axle(mounted: bool = False) -> Part:
    """Printed axle pin: through the tilt bearing from outside into the head's
    socket, clamping the inner ring against the collar with an M3 bolt.
    Flange down on the bed for printing, or mounted in the head frame"""
    b = p.TILT_BEARING
    shaft_l = b.width + p.MOVE_CLR + AXLE_SOCKET_DEPTH
    pin = Cylinder(COLLAR_R, AXLE_FLANGE_T, align=c.MIN)
    pin += Pos(0, 0, AXLE_FLANGE_T) * Cylinder(b.bore / 2 - 0.05, shaft_l, align=c.MIN)
    pin -= Cylinder(p.M3_CLEAR / 2, 2 * (shaft_l + AXLE_FLANGE_T))
    if not mounted:
        return pin
    # flange outside the bearing's outer face, shaft pointing -X into the head
    return Pos(ARM_X + b.width + AXLE_FLANGE_T, 0, 0) * Rot(0, -90, 0) * pin


# The fit test is the front of the head down to just behind both boards
FIT_TEST_Y0 = min(SR_Y, BOARD_Y) - p.PCB_T - 1.0 * MM


def make_fit_test() -> Part:
    """The front of the head front, cut just behind both boards: the face with
    its openings, pins and ribs plus a short ring of wall, to check the boards
    fit before printing the whole head"""
    return make_head_front() & c.box(-100, 100, FIT_TEST_Y0, 100, -100, 100)
