"""Which parts changed since a print? Compares the current gimbal_*.stl files
with the meshes inside a 3MF that was printed (by volume and surface area).

Usage (from python/):
    python tools/compare_parts.py ../3mf/printed/<the 3MF you printed>.3mf ../stl
Keep a copy of every 3MF you send to the printer in 3mf/printed/.
"""
import re, sys, zipfile, struct
import numpy as np
from xml.etree import ElementTree as ET
old3mf, new_dir = sys.argv[1], sys.argv[2]
ns = {'m': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}

def stats(tri):
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    vol = np.einsum('ij,ij->i', a, np.cross(b, c)).sum() / 6
    area = np.linalg.norm(np.cross(b - a, c - a), axis=1).sum() / 2
    return abs(vol), area

z = zipfile.ZipFile(old3mf)
cfg = z.read('Metadata/model_settings.config').decode()
old = {}
for obj in re.findall(r'<object id="\d+">.*?</object>', cfg, re.S):
    name = re.search(r'key="name" value="([^"]+)"', obj)[1].replace('gimbal_', '').replace('.stl', '')
    src = re.search(r'key="source_object_id" value="(\d+)"', obj)
    old[name] = obj
# map: objects in 3D/Objects/object_N.model, in the order of model_settings parts
models = sorted(n for n in z.namelist() if n.startswith('3D/Objects/'))
meshes = {}
for n in models:
    root = ET.fromstring(z.read(n))
    for o in root.iterfind('.//m:object', ns):
        v = np.array([[float(x.get(k)) for k in 'xyz'] for x in o.iterfind('.//m:vertex', ns)])
        t = np.array([[int(x.get(k)) for k in ('v1', 'v2', 'v3')] for x in o.iterfind('.//m:triangle', ns)])
        if len(t): meshes[n] = v[t]
def read_stl(p):
    d = open(p, 'rb').read(); n = struct.unpack('<I', d[80:84])[0]
    arr = np.frombuffer(d[84:84 + n * 50], dtype=np.dtype([('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')]))
    return arr['v'].reshape(-1, 3, 3).astype(float)
import glob, os
new = {os.path.basename(p)[7:-4]: stats(read_stl(p)) for p in glob.glob(f'{new_dir}/gimbal_*.stl')}
oldstats = [stats(m) for m in meshes.values()]
for name, (v, a) in sorted(new.items()):
    # match the printed mesh with the closest volume+area
    best = min(oldstats, key=lambda s: abs(s[0] - v) / v + abs(s[1] - a) / a)
    dv, da = v - best[0], a - best[1]
    changed = abs(dv) > 0.5 or abs(da) > 0.5
    print(f"{name:12s} volume {v:8.0f} (printed {best[0]:8.0f}, Δ {dv:+7.1f} mm³)  area Δ {da:+7.1f} mm²  {'CHANGED' if changed else 'same'}")
