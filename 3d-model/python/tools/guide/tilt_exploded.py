"""Exploded line drawing of the tilt joint for the assembly guide (SVG).

Usage (from python/): python tools/guide/tilt_exploded.py
Writes docs/drawings/tilt.svg.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))
from build123d import *
import gimbal_head as g, head, yoke, params as p, components as c
parts = g.place(0, 0)
hw = g.head_to_world(0, 0)
horn = c.mg90s_horn().moved(hw * head.HORN_LOC)
z = yoke.TILT_AXIS_Z
bolt = Pos(0, 0, z) * Rot(0, 90, 0) * Cylinder(1.5, 25, align=(Align.CENTER, Align.CENTER, Align.MIN))
bolt += Pos(0, 0, z) * Rot(0, 90, 0) * Cylinder(2.75, 3, align=(Align.CENTER, Align.CENTER, Align.MIN))
bolt = bolt.moved(Location((head.ARM_X + p.TILT_BEARING.width + head.AXLE_FLANGE_T, 0, 0)))
items = [
    (parts["head_front"], 0), (parts["yoke"], 0),
    (horn, (-4, 0, 34)), (parts["tilt_servo"], -40),
    (parts["pin_arm"], 22), (parts["tilt_bearing"], 14), (parts["tilt_axle"], 40), (bolt, 52),
]
shape = Compound([prt.moved(Location(d if isinstance(d, tuple) else (d, 0, 0))) for prt, d in items])
vis, hid = shape.project_to_viewport((-170, 300, 160), viewport_up=(0, 0, 1))
m = max(*Compound(children=vis).bounding_box().size)
exp = ExportSVG(scale=170 / m, margin=8)
exp.add_layer("v", line_weight=0.45)
exp.add_shape(vis, layer="v")
out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parents[2] / 'docs' / 'drawings' / 'tilt.svg'
out.parent.mkdir(exist_ok=True)
exp.write(str(out))
