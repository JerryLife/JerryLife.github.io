#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LATEX_DIR="$ROOT_DIR/assets/latex"
OUTPUT_PDF="$ROOT_DIR/assets/pdf/ZhaominWu.pdf"
WATCH_INTERVAL="${WATCH_INTERVAL:-2}"

if ! command -v make >/dev/null 2>&1; then
  echo "Error: make is not installed or not on PATH." >&2
  exit 127
fi

if ! command -v pdflatex >/dev/null 2>&1; then
  echo "Error: pdflatex is not installed or not on PATH." >&2
  exit 127
fi

build_pdf() {
  make -B -C "$LATEX_DIR"
  if [[ -f "$OUTPUT_PDF" ]]; then
    echo "Built: $OUTPUT_PDF"
  fi
}

snapshot_sources() {
  (
    cd "$LATEX_DIR"
    find . -maxdepth 2 -type f \( -name '*.tex' -o -name '*.cls' \) -print0 \
      | sort -z \
      | xargs -0 stat -c '%Y %n'
  )
}

watch_pdf() {
  local previous_snapshot current_snapshot

  echo "Watching $LATEX_DIR for LaTeX changes. Press Ctrl+C to stop."
  build_pdf
  previous_snapshot="$(snapshot_sources)"

  while true; do
    sleep "$WATCH_INTERVAL"
    current_snapshot="$(snapshot_sources)"
    if [[ "$current_snapshot" != "$previous_snapshot" ]]; then
      echo "Change detected. Rebuilding PDF..."
      build_pdf
      previous_snapshot="$current_snapshot"
    fi
  done
}

case "${1:-}" in
  watch)
    shift
    if [[ $# -gt 0 ]]; then
      echo "Error: watch mode does not accept extra arguments." >&2
      exit 2
    fi
    watch_pdf
    ;;
  "")
    build_pdf
    ;;
  *)
    make -B -C "$LATEX_DIR" "$@"
    ;;
esac
