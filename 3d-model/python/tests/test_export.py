import numpy as np
import pytest

from build123d import GeomType
from OCP.BRepAdaptor import BRepAdaptor_Surface

import gimbal_head as g
import params as p

PRINTED = ["base", "neck_cap", "pan_coupler", "yoke", "pin_arm", "head_front", "head_rear", "brows", "tilt_axle"]


def test_export_writes_printed_parts(tmp_path):
    files = g.export_all(tmp_path)
    names = sorted(f.name for f in files)
    assert names == sorted(f"gimbal_{n}.stl" for n in PRINTED)
    assert all(f.stat().st_size > 1000 for f in files)


def test_bushings_exported_when_bearings_off(tmp_path, monkeypatch):
    monkeypatch.setattr(p, "USE_PAN_BEARING", False)
    monkeypatch.setattr(p, "USE_TILT_BEARING", False)
    names = {f.name for f in g.export_all(tmp_path)}
    assert {"gimbal_pan_bushing.stl", "gimbal_tilt_bushing.stl"} <= names


@pytest.mark.parametrize("name", PRINTED)
def test_print_orientation_rests_on_bed(name):
    part = g.print_oriented(name)
    bb = part.bounding_box()
    assert bb.min.Z == pytest.approx(0, abs=1e-6)
    bed = [f for f in part.faces() if abs(f.center().Z) < 1e-4 and abs(f.normal_at().Z) > 0.99]
    assert sum(f.area for f in bed) > 50  # a real first layer, not a point


def test_support_flags_cover_printed_parts():
    assert set(g.printed_parts()) <= set(g.NEEDS_SUPPORT)
    assert {"pan_bushing", "tilt_bushing"} <= set(g.NEEDS_SUPPORT)


@pytest.mark.parametrize("name", PRINTED)
def test_printed_parts_have_no_loose_pieces(name):
    expected = 2 if name == "brows" else 1  # two brow rings on one plate
    assert len(g.BUILDERS[name]().solids()) == expected


def test_head_front_face_lies_on_the_bed():
    part = g.print_oriented("head_front")
    bed = [f for f in part.faces() if abs(f.center().Z) < 1e-4 and abs(f.normal_at().Z) > 0.99]
    assert sum(f.area for f in bed) > 1000  # the whole face, not just the brow rings



def steep_overhang_area(part, limit_deg=46, bridged_hole_r=4.5):
    """Downward faces leaning more than limit_deg from vertical (flatter than a
    45° chamfer), off the bed, that are not flat bridges: what a slicer would
    hold up with supports. Ceilings of small horizontal holes (radius up to
    bridged_hole_r) are left out: slicers bridge them"""
    total = 0.0
    for face in part.faces():
        if face.geom_type == GeomType.CYLINDER and BRepAdaptor_Surface(face.wrapped).Cylinder().Radius() <= bridged_hole_r:
            continue
        verts, tris = face.tessellate(0.05, 0.3)
        if not tris:
            continue
        v = np.array([[q.X, q.Y, q.Z] for q in verts])
        t = np.array(tris)
        a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
        n = np.cross(b - a, c - a)
        norm = np.linalg.norm(n, axis=1)
        nz = n[:, 2] / np.maximum(norm, 1e-12)
        zc = (a[:, 2] + b[:, 2] + c[:, 2]) / 3
        steep = (nz < -np.sin(np.radians(limit_deg))) & (nz > -0.99) & (zc > 0.3)
        total += float((norm[steep] / 2).sum())
    return total


@pytest.mark.parametrize("name", [n for n in PRINTED if not g.NEEDS_SUPPORT[n]])
def test_prints_without_support(name):
    assert steep_overhang_area(g.print_oriented(name)) < 10, name


def test_yoke_overhangs_stay_small():
    # it gets supports at the user's request, but must not grow new overhangs
    assert steep_overhang_area(g.print_oriented("yoke")) < 60


def test_support_settings():
    # the yoke's short bridges print unsupported, but the user wants the slicer's
    # supports there anyway; everything else prints bare
    assert {n for n, on in g.NEEDS_SUPPORT.items() if on} == {"yoke", "base"}


def test_cantilevers_are_gone():
    # flat undersides hanging high above the bed (not short bridges)
    part = g.print_oriented("yoke")
    tall = [f for f in part.faces() if f.center().Z > 30 and f.area > 150 and f.normal_at(f.center()).Z < -0.99]
    assert not tall, [round(f.area) for f in tall]


def test_brims_where_parts_are_tall_for_their_footprint():
    # height / sqrt(bed contact): yoke 4.7, tilt axle 1.4, every other part under 0.8
    assert g.NEEDS_BRIM == {"yoke", "tilt_axle"}


def islands(part, step=0.2):
    """Places where a layer starts with nothing under it (a floating start)"""
    from build123d import Box, Pos
    bb = part.bounding_box()
    found, prev, z = [], None, step / 2
    while z < bb.max.Z:
        cut = part & (Pos(0, 0, z) * Box(1000, 1000, 0.05))
        faces = [f for f in cut.faces() if abs(f.normal_at().Z) > 0.99 and f.center().Z < z]
        if prev is not None:
            for f in faces:
                below = Pos(0, 0, -step) * f
                if sum(getattr(below & s, "area", 0) or 0 for s in prev) < 1e-3:
                    found.append((round(z, 1), round(f.center().X, 1), round(f.center().Y, 1)))
        prev, z = faces, z + step
    return found


def test_base_has_no_floating_starts():
    assert islands(g.print_oriented("base")) == []


def test_travel_avoids_crossing_holes():
    import make_3mf
    assert make_3mf.process_overrides["reduce_crossing_wall"] == "1"


def test_fit_test_exported_on_its_own(tmp_path):
    f = g.export_fit_test(tmp_path)
    assert f.name == "gimbal_fit_test.stl" and f.stat().st_size > 1000
    assert "fit_test" not in g.printed_parts()  # not on the main plate



def test_print_settings_against_stringing():
    import make_3mf
    assert make_3mf.process_overrides["reduce_crossing_wall"] == "1"
    assert make_3mf.filament_overrides["nozzle_temperature"] == ["210"]


def test_fit_test_has_its_own_project():
    import make_3mf
    models = make_3mf.fit_test_models()
    assert [m.name for m in models] == ["gimbal_fit_test.stl"]
    assert make_3mf.FIT_TEST_OUTPUT.name == "gimbal_fit_test.3mf"
