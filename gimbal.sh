#!/usr/bin/env bash
# Runs the gimbal model's everyday tasks. See ./gimbal.sh help.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL="$ROOT/3d-model"
VIEWER_PORT=3939
BAMBU=/Applications/BambuStudio.app

usage() {
  cat <<EOF
Usage: ./gimbal.sh <command> [options]

  viewer                     start the OCP viewer (http://localhost:$VIEWER_PORT) and leave it running
  build [--pan N --tilt N]   motion checks, write the STLs to 3d-model/stl/, and show the assembly in the viewer
                             (pan -90..90, tilt -45..90, both default 0)
  3mf                        build 3d-model/3mf/gimbal_head.3mf and gimbal_fit_test.3mf from the STLs
                             (run build first so the STLs are current)

Python: uses \$PYTHON if set, else .venv/bin/python in 3d-model/ or in this
folder, else python3. It must have build123d installed.
EOF
}

find_python() {
  local candidates=()
  [[ -n "${PYTHON:-}" ]] && candidates+=("$PYTHON")
  candidates+=("$MODEL/.venv/bin/python" "$ROOT/.venv/bin/python" "$(command -v python3 || true)")
  for py in "${candidates[@]}"; do
    if [[ -x "$py" ]] && "$py" -c "import build123d" 2>/dev/null; then
      echo "$py"
      return
    fi
  done
  echo "error: no Python with build123d found; set PYTHON=/path/to/venv/bin/python" >&2
  exit 1
}

viewer() {
  if lsof -nP -iTCP:"$VIEWER_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "the viewer is already running: http://localhost:$VIEWER_PORT"
    return
  fi
  local py bin
  py="$(find_python)"
  bin="$(dirname "$py")/ocp-viewer"  # installed next to the interpreter
  [[ -x "$bin" ]] || bin="$(command -v ocp-viewer || true)"
  if [[ -z "$bin" ]]; then
    echo "error: ocp-viewer not found next to $py or on PATH" >&2
    exit 1
  fi
  echo "viewer on http://localhost:$VIEWER_PORT (Ctrl-C to stop)"
  exec "$bin"
}

build() {
  local py
  py="$(find_python)"
  cd "$MODEL/python"
  "$py" gimbal_head.py "$@"
}

make_3mf() {
  if [[ ! -d "$BAMBU" ]]; then
    echo "error: Bambu Studio not found at $BAMBU" >&2
    exit 1
  fi
  local py
  py="$(find_python)"
  cd "$MODEL/python"
  "$py" make_3mf.py
}

case "${1:-help}" in
  viewer) viewer ;;
  build) shift; build "$@" ;;
  3mf) make_3mf ;;
  help | -h | --help) usage ;;
  *) echo "unknown command: $1" >&2; usage >&2; exit 1 ;;
esac
