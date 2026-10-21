"""
Every dimension of the Wall-E camera head gimbal in one place.

Measure your own parts and correct the values here; all parts rebuild from
them. Values marked "measure" are typical numbers, not taken from your parts.

Board positions are as seen from the FRONT (looking into the camera), with
USB-C at the bottom, measured from the board's top-left corner.
"""

from dataclasses import dataclass

from build123d import MM


@dataclass(frozen=True)
class Bearing:
    bore: float
    od: float
    width: float


# ------------------------------------------------------- ESP32-S3-CAM board
BOARD_W = 30.4 * MM  # upright: width across, height top to bottom
BOARD_H = 38.4 * MM
PCB_T = 1.6 * MM
BOARD_HOLE_INSET = 3.2 * MM  # hole centres from each edge (24 x 32 mm pattern)
BOARD_HOLE_D = 3.0 * MM
# Camera module near the top edge (lens position and diameters measured on the board)
LENS_D = 7.94 * MM  # lens barrel, back step (the front step is 7.0)
LENS_D_FRONT = 7.0 * MM
LENS_X = BOARD_W - (19.0 * MM - LENS_D / 2)  # lens left side is 19 mm from the board's right edge
LENS_Y = 13.0 * MM - LENS_D / 2  # lens bottom is 13 mm below the top edge
CAM_MODULE = 8.5 * MM  # square module footprint (estimate)
LENS_TIP_H = 8.65 * MM - PCB_T  # lens tip above the PCB's front face (measured: 8.65 with the PCB)
CAM_BLOCK_H = LENS_TIP_H - 1.0 * MM  # front of the square camera block (estimate: the barrel is ~1 mm)
# Flash LEDs, on the camera's row
LED_W = 2.0 * MM  # measured
LED_XS = (9.0 * MM, BOARD_W - 7.0 * MM)  # left LED's right side 10 mm from the left edge, right LED's left side 8 mm from the right edge
LED_Y = 6.5 * MM  # (estimate, moved up after the fit test; the slots leave a margin around it)
# Status ("active") LED in the top-left corner, beside the mounting hole (measured)
STATUS_LED_W = 2.0 * MM
STATUS_LED = (7.0 * MM - STATUS_LED_W / 2, 4.0 * MM - STATUS_LED_W / 2)  # right side 7 mm from the left edge, bottom edge 4 mm from the top
LED_WIN_CLR = 1.0 * MM  # margin around every LED in the face, so the light shows even if a position is a bit off
# microSD socket at the top-left; the card goes in from the left edge
SD_X0 = 2.7 * MM
SD_Y0 = 5.8 * MM
SD_SHELL_W = 4.8 * MM
SD_SHELL_L = 10.6 * MM
SD_SHELL_H = 4.8 * MM - PCB_T  # measured: 4.8 with the PCB
SD_CLR = 0.5 * MM  # extra margin all round the card in the head's SD slot
SD_CARD_W = 11.0 * MM
SD_CARD_T = 1.0 * MM
SD_CARD_OUT = 4.0 * MM  # how far the inserted card sticks out past the edge (measure)
SD_FINGER = 6.0 * MM  # room for a fingertip beyond the card
# USB-C receptacle, centred on the bottom edge, and the cable plug used to flash
USB_W = 9.0 * MM
USB_H = 4.85 * MM - PCB_T  # measured: 4.85 with the PCB
USB_OVERHANG = 0.8 * MM
USB_PLUG_W = 12.5 * MM
USB_PLUG_T = 7.5 * MM
USB_PLUG_L = 25.0 * MM
# BOOT (left) and RESET (right) buttons beside the USB-C
BTN_XS = (8.1 * MM, 22.9 * MM)
BTN_Y = 32.9 * MM
PINHOLE_D = 2.0 * MM
# Header pins along the left and right edges, pointing out the back
HDR_X_INSET = 1.3 * MM
HDR_PITCH = 2.54 * MM
HDR_COUNT = 8
HDR_Y0 = 7.9 * MM
HDR_BACK = 8.5 * MM  # plastic spacer + pin length behind the PCB
DUPONT_L = 14.0 * MM
DUPONT_W = 2.6 * MM  # Dupont housing, 2.54 mm square per pin plus a little
BAY_DEPTH = 30.7 * MM  # free depth behind the PCB for pins, plugs and wire bends

# ------------------------------------------------------------- HC-SR04 (measure)
SR_W = 45.0 * MM
SR_H = 20.0 * MM
SR_PCB_T = 1.6 * MM
SR_TX_D = 16.2 * MM  # transducer can diameter
SR_TX_H = 12.0 * MM  # transducer height in front of the PCB (the head allows up to +0.5 mm)
SR_CLR = 0.5 * MM  # clearance all round the board in the head (printed parts come out a bit tight)
CAN_OUT = 1.5 * MM  # how far the transducer cans stand out of the face (inside the brow rings)
SR_TX_DX = 26.0 * MM  # transducer centre spacing
SR_PIN_LEN = 6.0 * MM  # pins leave the bottom edge pointing down, in the PCB plane
SR_BACK_H = 3.0 * MM  # components on the back
SR_HOLE_D = 2.0 * MM  # corner mounting holes (measured), M2 screws go through them
SR_HOLE_INSET = 1.6 * MM  # hole centres from the board's edges (estimate from a photo)

# ------------------------------------------------------------ SYD1230 laser
LASER_D = 12.0 * MM  # measured
LASER_L = 35.0 * MM

# --------------------------------------------------------------- MG90S servo
SERVO_L = 22.8 * MM
SERVO_W = 12.2 * MM
SERVO_H = 22.7 * MM  # body bottom to case top
SERVO_TAB_L = 32.3 * MM
SERVO_TAB_T = 2.5 * MM
SERVO_TAB_Z = 15.9 * MM  # tab underside above the body bottom
SERVO_TAB_HOLE_PITCH = 27.8 * MM
SERVO_SHAFT_OFFSET = 5.9 * MM  # shaft centre from the near body end
SERVO_SHAFT_H = 4.0 * MM  # spline top above the case top
# Double-arm horn supplied with the MG90S (measure yours)
HORN_HUB_D = 7.2 * MM
HORN_HUB_H = 4.4 * MM
HORN_ARM_L = 16.0 * MM  # hub centre to arm tip
HORN_ARM_W_HUB = 6.0 * MM
HORN_ARM_W_TIP = 4.0 * MM
HORN_ARM_T = 1.8 * MM

# ---------------------------------------------------------------- bearings
PAN_BEARING = Bearing(8 * MM, 22 * MM, 7 * MM)  # 608
TILT_BEARING = Bearing(8 * MM, 22 * MM, 7 * MM)  # 608; its axle is a printed pin (bore must be ≥ 6 mm)
USE_PAN_BEARING = True  # False prints a bushing of the same size instead
USE_TILT_BEARING = True
M3_CLEAR = 3.4 * MM  # bolt through the tilt axle pin
PIN_ARM_REACH = TILT_BEARING.od / 2 + 2 * MM  # the slim arm's boss above the tilt axis

# ------------------------------------- base plate (same as the reference gimbal)
BASE_L = 41.8 * MM
BASE_W = 30.8 * MM
BASE_CORNER_R = 3.0 * MM
BASE_HOLE_D = 2.2 * MM  # M2
BASE_HOLE_DX = 22.0 * MM
BASE_HOLE_DY = 33.0 * MM
BASE_CBORE_D = 4.4 * MM
BASE_CBORE_DEPTH = 2.2 * MM
BASE_BOSS_H = 4.4 * MM
BASE_PLATE_T = 2.4 * MM
BASE_LONG_AXIS = "Y"  # world axis the 41.8 mm side runs along ("X" or "Y")

# ---------------------------------------------------------- motion and fits
PAN_RANGE = (-90, 90)
TILT_RANGE = (-45, 90)  # degrees from level, + looks up
FIT = 0.25 * MM  # sliding clearance
PRESS = 0.05 * MM  # bearing seat diameter = od + PRESS
MOVE_CLR = 0.5 * MM  # minimum gap between moving and static parts
WALL = 2.0 * MM
HEAD_WALL = 1.6 * MM  # head shell wall; the HC-SR04 plus these walls sets the head width
M2_CLEAR = 2.2 * MM
M2_PILOT = 1.7 * MM

# ------------------------------------------------------------------- wires
WIRE_COUNT = 13
WIRE_D = 1.4 * MM
WIRE_FILL = 0.4  # bundle area / hole area where the wires must slide
PLUG_W = 7.6 * MM  # 3-pin Dupont housing (servo plug), must pass the wire holes
PLUG_T = 2.54 * MM
WIRE_ANGLE = 180  # where the wires cross the pan joint, degrees from +X (180 = the servo side, -X)
SLOT_MARGIN = 15  # degrees of extra wire slot past each end of the pan travel
