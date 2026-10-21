"""Build docs/ASSEMBLY_GUIDE.pdf from the text below and the SVG drawings.

Needs reportlab and svglib in the project venv. Usage (from python/):
    python tools/guide/stages.py
    python tools/guide/tilt_exploded.py
    python tools/guide/make_guide.py
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (KeepTogether, ListFlowable, ListItem, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)
from svglib.svglib import svg2rlg

HERE = Path(__file__).resolve().parent
DOCS = HERE.parents[2] / "docs"
S = DOCS / "drawings"  # written by stages.py and tilt_exploded.py
OUT = str(DOCS / "ASSEMBLY_GUIDE.pdf")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=20, spaceAfter=6, textColor=colors.HexColor("#1f3a5f"))
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=14, spaceBefore=10, spaceAfter=4, textColor=colors.HexColor("#1f3a5f"))
B = ParagraphStyle("B", parent=ss["BodyText"], fontSize=10, leading=14)
SM = ParagraphStyle("SM", parent=B, fontSize=8.5, leading=11, textColor=colors.HexColor("#555555"))
TIP = ParagraphStyle("TIP", parent=B, backColor=colors.HexColor("#fff6d6"), borderPadding=5, spaceBefore=4, spaceAfter=8)
CELL = ParagraphStyle("CELL", parent=B, fontSize=9, leading=12)

def img(name, width=62 * mm):
    d = svg2rlg(f"{S}/{name}.svg")
    s = width / d.width
    d.scale(s, s); d.width *= s; d.height *= s
    return d

def table(rows, widths, header=True):
    t = Table([[Paragraph(str(c), CELL) for c in r] for r in rows], colWidths=widths, repeatRows=1 if header else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#bbbbbb")), ("VALIGN", (0, 0), (-1, -1), "TOP")]
    if header:
        st.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef6")))
    t.setStyle(TableStyle(st))
    return t

def step(n, title, body, pic=None, tip=None):
    text = [Paragraph(f"Step {n}: {title}", H2)]
    for para in body:
        text.append(Paragraph(para, B))
    if tip:
        text.append(Paragraph(f"<b>Tip:</b> {tip}", TIP))
    if pic:
        t = Table([[text, img(pic)]], colWidths=[108 * mm, 66 * mm])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
        return KeepTogether([t, Spacer(1, 6)])
    return KeepTogether(text)

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
                        title="Wall-E camera head gimbal: assembly guide", author="Claude")
f = []
f += [Paragraph("Wall-E camera head gimbal", H1), Paragraph("Assembly guide", ss["Heading3"]),
      Paragraph("Pan/tilt head for an RC tank: ESP32-S3-CAM, HC-SR04 and SYD1230 laser on two MG90S servos, both axes on 608 bearings. "
                "Print everything first (printing notes at the end), then follow the steps in order. "
                "Directions: +X is to the right seen from behind the tank; the camera looks toward +Y. "
                "The SD card side of the head is +X; the tilt servo is in the -X arm.", B),
      Spacer(1, 6), img("s7", 55 * mm), Spacer(1, 4)]

f.append(Paragraph("Parts to print", H2))
f.append(table([
    ["File", "What it is", "Support / brim"],
    ["gimbal_base.stl", "Plate with the reference gimbal's footprint plus the drum neck", "supports"],
    ["gimbal_neck_cap.stl", "Holds the pan bearing; wire slot", "none"],
    ["gimbal_pan_coupler.stl", "Takes the pan servo horn; stub carries the yoke", "none"],
    ["gimbal_yoke.stl", "Crossbar and the -X arm for the tilt servo", "supports + brim"],
    ["gimbal_pin_arm.stl", "Slim +X arm with the tilt bearing", "none"],
    ["gimbal_head_front.stl", "Face, eyes, camera, laser clamp, side joints", "none"],
    ["gimbal_head_rear.stl", "Back cover", "none"],
    ["gimbal_brows.stl", "Two brow tubes around the eyes", "none"],
    ["gimbal_tilt_axle.stl", "Tilt axle pin", "brim"],
], [48 * mm, 90 * mm, 34 * mm]))

f.append(Paragraph("Bought parts and hardware", H2))
f.append(table([
    ["Qty", "Item", "Used for"],
    ["2", "MG90S servo (with double-arm horns and tab screws)", "pan and tilt. Tab screws no longer than 6 mm"],
    ["2", "608 bearing (8 x 22 x 7 mm)", "pan and tilt (printed bushings can stand in)"],
    ["1", "ESP32-S3-CAM, HC-SR04, SYD1230 laser, Dupont jumper wires", "electronics"],
    ["1", "M3 x 25 bolt + nut + washer", "through the tilt axle pin; nut inside the head"],
    ["2", "M3 x 12", "pin arm to the crossbar, from below"],
    ["4", "M2 x 16", "neck cap to neck"],
    ["1", "M2 x 8", "yoke to coupler stub"],
    ["2", "M2 x 8", "rear cover, bottom (from behind)"],
    ["2", "M2 x 6", "rear cover, top (from above, through the top wall)"],
    ["1", "M2 x 10", "laser clamp"],
    ["4", "M2 x 6", "HC-SR04 to its corner posts (through its corner holes)"],
    ["2", "M2 x 6", "camera board, at the two corners without a pin"],
    ["4", "M2 (length to suit)", "base plate to the tank cover"],
], [12 * mm, 90 * mm, 70 * mm]))

f.append(step(1, "Fix the base", ["Screw the base to the tank cover through the open drum, using the four M2 screws in the corner counterbores. "
                                   "Do this first: the screws are driven from above before anything goes inside."], "s1"))
f.append(step(2, "Pan servo", ["The servo's cable leaves the shaft end of its body. Thread the plug through the arch at the bottom of the front pillar and down "
                                "the plate's front cable hole. Stand the servo on the plate with its shaft on the pan axis, and screw its tabs to the front pillar "
                                "and the rear ledge."], "s2",
              "Centre the servo (90°) before the next step, so pan 0° is straight ahead."))
f.append(step(3, "Neck cap and coupler", [
    "Press a 608 bearing into the neck cap. Set the pan servo's horn on the centred spline, arms across the -X direction. "
    "Push the coupler's stub up through the bearing from below, then lower cap and coupler onto the neck so the horn drops into the coupler's pocket. "
    "The coupler's wire hole must face -X. Screw the cap down with 4 x M2 x 16."], "s3"))
f.append(step(4, "Yoke and pin arm", [
    "Fit the yoke on the coupler's stub (the flat keys it) and fix it with the central M2 x 8. "
    "Press a 608 into the pin arm from its inner side, then bolt the arm onto the crossbar's +X end with 2 x M3 x 12 from below."], "s4"))

f.append(step(5, "Head: electronics", [
    "Fit the camera board on its two pins (camera through the face, USB-C pointing down) and screw its other two corners with 2 x M2 x 6, so it can't slide back. Slide the HC-SR04 in from the back, cans first, until its board rests "
    "on the four corner posts (the cans stand out through the face) and screw it to them with 4 x M2 x 6 through its corner holes, "
    "and seat the brow tubes in the recesses around the eye openings, over the cans (a drop of glue holds them). "
    "Push the laser into its clamp on top; aim it later, then tighten the clamp's M2 screw."], "s5"))
f.append(step(6, "Wires", [
    "Plug the Dupont leads onto the camera board and the HC-SR04 inside the head, and pass them out of the slot in the head's underside (on the -X side). "
    "The laser's two wires come in behind its clamp."],
    None, "Up to 13 wires leave the head. Keep them loose enough to slide through the wire holes as the head tilts."))
f.append(step(7, "Tilt joint", [
    "Press the tilt servo's horn into the pocket on the head's -X side. Hold the head between the arms, push the axle pin from outside through the 608 into the head's socket, "
    "and bolt it: M3 x 25 from outside, washer and nut inside the head (reach it through the open back). "
    "Centre the tilt servo, level the head, and slide the servo into the -X arm from outside so its spline enters the horn; screw its tabs. "
    "Close the head with the rear cover: its rim drops inside the head's opening and lines it up, then 2 x M2 x 8 at the bottom from behind and 2 x M2 x 6 "
    "from above through the top wall. In the drawing, from left to right: M3 bolt, axle pin, pin arm with the 608, head (the horn floats above its pocket), "
    "servo housing on the yoke (open on the outside), tilt servo."], "tilt",
    "Don't overtighten the M3 on a printed bushing: it clamps it."))
f.append(step(8, "Cable routing", [
    "Run the tilt servo's cable down the -X arm into the tunnel in the crossbar. Feed it and the head's bundle down the yoke's wire hole, "
    "through the cap's slot and the coupler's hole, and out of the base through the plate's front hole. "
    "Leave slack in the drum: the bundle slides through the holes as the head tilts."]))

f.append(Paragraph("Checks before powering up", H2))
f.append(ListFlowable([ListItem(Paragraph(t, B)) for t in [
    "Turn the head by hand through pan -90° to +90° and tilt -45° (down) to +90° (up). Nothing should rub, and wires must not pull.",
    "Pan: positive turns right (+X). Tilt: positive looks up. Calibrate the servo angles for straight ahead in software.",
    "The USB-C port is on the underside of the head; the SD card slides in from the +X side.",
    "Laser: adjust the clamp until the dot sits at the image centre, then tighten.",
]], bulletType="bullet"))

f.append(Paragraph("Electronics notes", H2))
f.append(ListFlowable([ListItem(Paragraph(t, B)) for t in [
    "HC-SR04 Echo is a 5 V signal: put a divider (for example 1k / 2k) before the ESP32 input.",
    "The laser draws about 30-40 mA: switch it with a transistor or MOSFET module, not straight from a GPIO pin.",
    "Power the servos from a separate 5 V supply (about 1 A), with grounds shared.",
]], bulletType="bullet"))

f.append(Paragraph("Printing notes", H2))
f.append(Paragraph("Bambu Lab A1, 0.4 mm nozzle, 0.16 mm High Quality, PLA. Open gimbal_head.3mf for the settings already applied "
                   "(one plate, about 5 h and 80 g). Print orientations: neck cap upside down, head front face down, pin arm on its outer face, "
                   "yoke lying on the servo arm's outer face. The measured values (horn, HC-SR04, camera) are estimates: "
                   "check them against your parts in params.py before printing.", B))

doc.build(f)
print("ok")
