"""
Reference models of the bought parts, and the volumes around them that the
printed parts must leave empty (keep-outs). Simple boxes and cylinders only.

Each function returns a Part in the component's own frame; the printed-part
modules publish Locations that place these frames.
"""

from build123d import *

import params as p

MIN = (Align.CENTER, Align.CENTER, Align.MIN)


def box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part:
    """Axis-aligned box between two corners"""
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def cyl_y(r: float, y0: float, y1: float, x: float = 0, z: float = 0) -> Part:
    """Cylinder along Y from y0 to y1"""
    return Pos(x, y0, z) * Rot(-90, 0, 0) * Cylinder(r, y1 - y0, align=MIN)


# ------------------------------------------------------------- ESP32-S3-CAM
# Frame: origin at the centre of the PCB's front face, camera looking +Y,
# USB-C toward -Z, SD side toward +X (the viewer's left when facing the camera)


def board_x(fx: float) -> float:
    """X of a point measured from the board's left edge as seen from the front"""
    return p.BOARD_W / 2 - fx


def board_z(fy: float) -> float:
    """Z of a point measured from the board's top edge"""
    return p.BOARD_H / 2 - fy


def esp32_board() -> Part:
    pcb = box(-p.BOARD_W / 2, p.BOARD_W / 2, -p.PCB_T, 0, -p.BOARD_H / 2, p.BOARD_H / 2)
    for hx in (-1, 1):
        for hz in (-1, 1):
            hole = Pos(hx * (p.BOARD_W / 2 - p.BOARD_HOLE_INSET), 0, hz * (p.BOARD_H / 2 - p.BOARD_HOLE_INSET))
            pcb -= hole * Rot(90, 0, 0) * Cylinder(p.BOARD_HOLE_D / 2, 3 * p.PCB_T)
    lx, lz = board_x(p.LENS_X), board_z(p.LENS_Y)
    cam = box(lx - p.CAM_MODULE / 2, lx + p.CAM_MODULE / 2, 0, p.CAM_BLOCK_H, lz - p.CAM_MODULE / 2, lz + p.CAM_MODULE / 2)
    lens_step = p.CAM_BLOCK_H + 0.6 * MM
    cam += cyl_y(p.LENS_D / 2, 0, lens_step, lx, lz) + cyl_y(p.LENS_D_FRONT / 2, 0, p.LENS_TIP_H, lx, lz)
    sd = box(
        board_x(p.SD_X0 + p.SD_SHELL_W), board_x(p.SD_X0), 0, p.SD_SHELL_H,
        board_z(p.SD_Y0 + p.SD_SHELL_L), board_z(p.SD_Y0),
    )
    leds = [
        box(board_x(x) - p.LED_W / 2, board_x(x) + p.LED_W / 2, 0, 0.8, board_z(p.LED_Y) - p.LED_W / 2, board_z(p.LED_Y) + p.LED_W / 2)
        for x in p.LED_XS
    ]
    sx, sy = p.STATUS_LED
    leds.append(box(board_x(sx) - p.STATUS_LED_W / 2, board_x(sx) + p.STATUS_LED_W / 2, 0, 0.8,
                    board_z(sy) - p.STATUS_LED_W / 2, board_z(sy) + p.STATUS_LED_W / 2))
    usb_z0 = -p.BOARD_H / 2 - p.USB_OVERHANG
    usb = box(-p.USB_W / 2, p.USB_W / 2, 0, p.USB_H, usb_z0, usb_z0 + 7.3 * MM)
    buttons = [
        box(board_x(x) - 1.5, board_x(x) + 1.5, 0, 1.5, board_z(p.BTN_Y) - 1.5, board_z(p.BTN_Y) + 1.5)
        for x in p.BTN_XS
    ]
    pins = []
    for sx in (-1, 1):
        x = sx * (p.BOARD_W / 2 - p.HDR_X_INSET)
        z_top = board_z(p.HDR_Y0) + 1.27
        z_bot = board_z(p.HDR_Y0 + (p.HDR_COUNT - 1) * p.HDR_PITCH) - 1.27
        pins.append(box(x - 1.27, x + 1.27, -p.PCB_T - 2.5, -p.PCB_T, z_bot, z_top))  # spacer
        for i in range(p.HDR_COUNT):
            z = board_z(p.HDR_Y0 + i * p.HDR_PITCH)
            pins.append(box(x - 0.32, x + 0.32, -p.PCB_T - p.HDR_BACK, -p.PCB_T, z - 0.32, z + 0.32))
    return pcb + [cam, sd, *leds, usb, *buttons, *pins]


def esp32_keepout() -> Part:
    """Board plus the Dupont bay behind it, with room beside the header rows
    for the plugs' wires"""
    bay = box(-p.BOARD_W / 2, p.BOARD_W / 2, -p.BAY_DEPTH, -p.PCB_T, -p.BOARD_H / 2, p.BOARD_H / 2)
    x = p.BOARD_W / 2 - p.HDR_X_INSET + p.DUPONT_W / 2 + 1.0 * MM
    z_top = board_z(p.HDR_Y0) + p.HDR_PITCH / 2 + 1.0 * MM
    z_bot = board_z(p.HDR_Y0 + (p.HDR_COUNT - 1) * p.HDR_PITCH) - p.HDR_PITCH / 2 - 1.0 * MM
    plugs = box(-x, x, -p.BAY_DEPTH, -p.PCB_T, z_bot, z_top)
    return esp32_board() + bay + plugs


def sd_access(grow: float = 0.0) -> Part:
    """The inserted card sticking out past the +X edge, and a fingertip beyond it;
    grow adds a margin all round (except at the board's edge)"""
    x0 = p.BOARD_W / 2
    zc = board_z(p.SD_Y0 + p.SD_SHELL_L / 2)
    card = box(x0, x0 + p.SD_CARD_OUT + grow, -grow, p.SD_SHELL_H + grow, zc - p.SD_CARD_W / 2 - grow, zc + p.SD_CARD_W / 2 + grow)
    x1 = x0 + p.SD_CARD_OUT
    finger = box(x1, x1 + p.SD_FINGER + grow, -3 * MM - grow, p.SD_SHELL_H + 3 * MM + grow,
                 zc - p.SD_CARD_W / 2 - 1 - grow, zc + p.SD_CARD_W / 2 + 1 + grow)
    return card + finger


def usb_plug() -> Part:
    """USB-C cable plug overmold, plugged in from below"""
    z1 = -p.BOARD_H / 2 - p.USB_OVERHANG
    yc = p.USB_H / 2
    return box(
        -p.USB_PLUG_W / 2, p.USB_PLUG_W / 2, yc - p.USB_PLUG_T / 2, yc + p.USB_PLUG_T / 2,
        z1 - p.USB_PLUG_L, z1,
    )


# ------------------------------------------------------------------ HC-SR04
# Frame: origin at the centre of the PCB's front face, transducers along X
# pointing +Y, pins toward -Z


def sr_holes() -> list[tuple[float, float]]:
    """HC-SR04 corner mounting holes (x, z) in its own frame"""
    dx, dz = p.SR_W / 2 - p.SR_HOLE_INSET, p.SR_H / 2 - p.SR_HOLE_INSET
    return [(sx * dx, sz * dz) for sx in (-1, 1) for sz in (-1, 1)]


def hcsr04() -> Part:
    pcb = box(-p.SR_W / 2, p.SR_W / 2, -p.SR_PCB_T, 0, -p.SR_H / 2, p.SR_H / 2)
    for hx, hz in sr_holes():
        pcb -= cyl_y(p.SR_HOLE_D / 2, -2 * p.SR_PCB_T, p.SR_PCB_T, hx, hz)
    cans = [cyl_y(p.SR_TX_D / 2, 0, p.SR_TX_H, sx * p.SR_TX_DX / 2) for sx in (-1, 1)]
    pin_w = 4 * 2.54 * MM
    pins = box(-pin_w / 2, pin_w / 2, -p.SR_PCB_T / 2 - 0.32, -p.SR_PCB_T / 2 + 0.32, -p.SR_H / 2 - p.SR_PIN_LEN, -p.SR_H / 2)
    back = box(-p.SR_W / 2 + 3, p.SR_W / 2 - 3, -p.SR_PCB_T - p.SR_BACK_H, -p.SR_PCB_T, -p.SR_H / 2 + 2, p.SR_H / 2 - 2)
    return pcb + cans + pins + back


def hcsr04_keepout() -> Part:
    """Sensor plus its Dupont plugs below the pins and the parts on its back"""
    plug_w = 4 * 2.54 * MM + 2 * MM
    plugs = box(
        -plug_w / 2, plug_w / 2, -p.SR_PCB_T / 2 - p.DUPONT_W / 2 - 0.3, -p.SR_PCB_T / 2 + p.DUPONT_W / 2 + 0.3,
        -p.SR_H / 2 - p.DUPONT_L - 8 * MM, -p.SR_H / 2,
    )
    # the parts on the back; the corners (mounting holes) stay free
    back = box(-p.SR_W / 2 + 3, p.SR_W / 2 - 3, -p.SR_PCB_T - p.SR_BACK_H, -p.SR_PCB_T, -p.SR_H / 2 + 2, p.SR_H / 2 - 2)
    return hcsr04() + plugs + back


# -------------------------------------------------------------------- laser
# Frame: origin at the centre of the rear end, beam along +Y


def laser() -> Part:
    return cyl_y(p.LASER_D / 2, 0, p.LASER_L)


# -------------------------------------------------------------------- MG90S
# Frame: origin on the shaft axis in the plane of the case top, shaft along +Z,
# long side along X with the body extending toward -X


def servo_body_x() -> float:
    """X of the body centre (the shaft sits near the +X end)"""
    return -(p.SERVO_L / 2 - p.SERVO_SHAFT_OFFSET)


def mg90s() -> Part:
    cx = servo_body_x()
    body = box(cx - p.SERVO_L / 2, cx + p.SERVO_L / 2, -p.SERVO_W / 2, p.SERVO_W / 2, -p.SERVO_H, 0)
    tab_z0 = -p.SERVO_H + p.SERVO_TAB_Z
    tabs = box(cx - p.SERVO_TAB_L / 2, cx + p.SERVO_TAB_L / 2, -p.SERVO_W / 2, p.SERVO_W / 2, tab_z0, tab_z0 + p.SERVO_TAB_T)
    for sx in (-1, 1):
        tabs -= Pos(cx + sx * p.SERVO_TAB_HOLE_PITCH / 2, 0, tab_z0) * Cylinder(1.0, 10)
    shaft = Cylinder(2.4 * MM, p.SERVO_SHAFT_H, align=MIN)
    return body + tabs + shaft


def horn_arms_sketch(grow: float = 0.0) -> Sketch:
    """Outline of the horn's two arms seen from above, enlarged by grow"""
    with BuildSketch() as arm:
        with BuildLine():
            r0, r1 = p.HORN_ARM_W_HUB / 2 + grow, p.HORN_ARM_W_TIP / 2 + grow
            Polyline((-p.HORN_ARM_L, -r1), (0, -r0), (p.HORN_ARM_L, -r1),
                     (p.HORN_ARM_L, r1), (0, r0), (-p.HORN_ARM_L, r1), close=True)
        make_face()
        with Locations((-p.HORN_ARM_L, 0), (p.HORN_ARM_L, 0)):
            Circle(p.HORN_ARM_W_TIP / 2 + grow)
    return arm.sketch


def mg90s_horn(grow: float = 0.0) -> Part:
    """Double-arm horn; origin on the hub axis at the face that sits on the servo.
    grow enlarges it all round, for cutting the pocket that holds it"""
    hub = Pos(0, 0, -grow) * Cylinder(p.HORN_HUB_D / 2 + grow, p.HORN_HUB_H + 2 * grow, align=MIN)
    arms = Pos(0, 0, p.HORN_HUB_H - p.HORN_ARM_T - grow) * extrude(horn_arms_sketch(grow), p.HORN_ARM_T + 2 * grow)
    return hub + arms


# ------------------------------------------------------------------ bearing


def bearing(b: p.Bearing) -> Part:
    """Ring centred on the origin, axis Z"""
    return Cylinder(b.od / 2, b.width) - Cylinder(b.bore / 2, b.width)
