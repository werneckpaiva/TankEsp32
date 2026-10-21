"""
Build Bambu Studio projects from the STL files written by gimbal_head.py, with
printer, process and filament settings embedded and the plates already sliced:
gimbal_head.3mf (all printed parts) and gimbal_fit_test.3mf (the test piece).

STL files only hold geometry; a 3MF project also stores the print settings, so
it opens in Bambu Studio ready to print (or to tweak and re-slice).

Usage (from the python/ folder, after running gimbal_head.py):
    python make_3mf.py
Reads ../stl/ and writes the projects to ../3mf/.
"""

import json
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path

from gimbal_head import NEEDS_BRIM, NEEDS_SUPPORT, STL_DIR, THREEMF_DIR, printed_parts

bambu = Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")
profiles = Path.home() / "Library/Application Support/BambuStudio/system/BBL"

printer = "Bambu Lab A1 0.4 nozzle"
process = "0.16mm High Quality @BBL A1"
filament = "Bambu PLA Matte @BBL A1"
# The base and the yoke get supports (see gimbal_head.NEEDS_SUPPORT)
support = {
    "enable_support": "1",
    "support_type": "tree(auto)",
    "support_on_build_plate_only": "1",
}
no_support = {"enable_support": "0"}
no_brim = {"brim_type": "no_brim"}  # PLA on textured PEI holds without one
brim = {"brim_type": "outer_only", "brim_width": "5"}  # see gimbal_head.NEEDS_BRIM
# Changes on top of the process profile
# Travel goes around holes instead of across them, so it does not string over them
process_overrides = support | no_brim | {"curr_bed_type": "Textured PEI Plate", "reduce_crossing_wall": "1"}
# A cooler nozzle (the profile's default is 220 °C) strings less
filament_overrides = {"nozzle_temperature": ["210"]}

# Each model with the settings stored on its object, which apply whatever
# process preset is selected when the project is opened
models = {
    STL_DIR / f"gimbal_{name}.stl": (support if NEEDS_SUPPORT[name] else no_support)
    | (brim if name in NEEDS_BRIM else no_brim)
    for name in printed_parts()
}
output = THREEMF_DIR / "gimbal_head.3mf"  # Bambu Studio needs absolute paths
FIT_TEST_OUTPUT = THREEMF_DIR / "gimbal_fit_test.3mf"


def fit_test_models() -> dict[Path, dict]:
    """The face-only test piece, on its own plate"""
    return {STL_DIR / "gimbal_fit_test.stl": no_support | no_brim}


def load_profile(kind: str, name: str) -> dict:
    """Load a system profile with its 'inherits' chain merged in"""
    settings = json.loads((profiles / kind / f"{name}.json").read_text())
    parent = settings.pop("inherits", None)
    if parent:
        settings = load_profile(kind, parent) | settings
    return settings


def patch_project(path: Path, models: dict[Path, dict]) -> None:
    """Add per-object settings and mark the presets as modified copies of the
    system ones, so Bambu Studio doesn't fall back to the stock presets"""
    with zipfile.ZipFile(path) as zf:
        entries = [(info, zf.read(info)) for info in zf.infolist()]
    settings_by_name = {model.name: settings for model, settings in models.items()}

    def add_object_settings(match: re.Match) -> str:
        head, body = match[1], match[2]
        name = re.search(r'<metadata key="name" value="([^"]+)"/>', body)[1]
        settings = settings_by_name[name]
        for key in settings:  # drop values from an earlier pass
            body = re.sub(rf' *<metadata key="{key}" value="[^"]*"/>\n', "", body)
        extra = "".join(
            f'    <metadata key="{key}" value="{value}"/>\n'
            for key, value in settings.items()
        )
        return head + extra + body

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for info, data in entries:
            if info.filename == "Metadata/model_settings.config":
                data = re.sub(
                    r'(<object id="\d+">\n)(.*?</object>)',
                    add_object_settings,
                    data.decode(),
                    flags=re.DOTALL,
                ).encode()
            elif info.filename == "Metadata/project_settings.config":
                settings = json.loads(data)
                # order: process, filament(s), printer
                settings["inherits_group"] = [process, filament, printer]
                settings["different_settings_to_system"] = [
                    ";".join(sorted(process_overrides)), ";".join(sorted(filament_overrides)), ""
                ]
                data = json.dumps(settings, indent=4).encode()
            zf.writestr(info, data)


def build_project(models: dict[Path, dict], output: Path) -> None:
    """Arrange, configure and slice the models into a Bambu Studio project"""
    output.parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        files = {}
        for kind, name, overrides in [
            ("machine", printer, {}),
            ("process", process, process_overrides),
            ("filament", filament, filament_overrides),
        ]:
            files[kind] = Path(tmp) / f"{kind}.json"
            files[kind].write_text(json.dumps(load_profile(kind, name) | overrides))

        subprocess.run(
            [
                bambu,
                "--load-settings", f"{files['machine']};{files['process']}",
                "--load-filaments", str(files["filament"]),
                "--arrange", "1",
                "--orient", "0",  # keep the modelled (upright) orientation
                "--export-3mf", str(output),
                *map(str, models),
            ],
            check=True,
            capture_output=True,
            cwd=output.parent,  # the CLI writes result.json to the working directory
        )

    # Per-object settings only take effect when Bambu Studio loads a project, so
    # add them first, then reload and slice; patch again as slicing rewrites them
    patch_project(output, models)
    subprocess.run(
        [bambu, "--slice", "0", "--export-3mf", str(output), str(output)],
        check=True,
        capture_output=True,
        cwd=output.parent,
    )
    patch_project(output, models)
    print(f"{output.name} written")


def main() -> None:
    build_project(models, output)
    build_project(fit_test_models(), FIT_TEST_OUTPUT)


if __name__ == "__main__":
    main()
