"""Line drawings of the assembly stages for the assembly guide (SVG).

Usage (from python/): python tools/guide/stages.py
Writes the SVGs to docs/drawings/.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))
from build123d import *
import gimbal_head as g
out = sys.argv[1] if len(sys.argv) > 1 else str(HERE.parents[2] / 'docs' / 'drawings')
Path(out).mkdir(exist_ok=True)
parts = g.place(0, 0)
stages = {
  "s1": {"base"},
  "s2": {"base", "pan_servo"},
  "s3": {"base", "pan_servo", "neck_cap", "pan_bearing", "pan_coupler"},
  "s4": {"base", "pan_servo", "neck_cap", "pan_bearing", "pan_coupler", "yoke", "pin_arm", "tilt_bearing"},
  "s5": {"head_front", "board", "hcsr04", "laser", "brows"},
  "s7": set(parts),
}
for name, keep in stages.items():
    shape = Compound([parts[k] for k in keep])
    vis, hid = shape.project_to_viewport((300, 300, 220), viewport_up=(0, 0, 1))
    m = max(*Compound(children=vis + hid).bounding_box().size)
    exp = ExportSVG(scale=150 / m, margin=10)
    exp.add_layer("v", line_weight=0.6)
    exp.add_layer("h", line_color=(190, 190, 190), line_type=LineType.ISO_DOT, line_weight=0.15)
    exp.add_shape(vis, layer="v"); exp.add_shape(hid, layer="h")
    exp.write(f"{out}/{name}.svg")
