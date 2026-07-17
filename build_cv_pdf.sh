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
  {
    find "$LATEX_DIR" -maxdepth 2 -type f \( -name '*.tex' -o -name '*.cls' -o -name 'Makefile' \) -print0
    find "$ROOT_DIR/_data/content" -maxdepth 2 -type f -name '*.yml' -print0
    find "$ROOT_DIR/_data/content/publications" -maxdepth 1 -type f -name '*.bib' -print0
    printf '%s\0' "$ROOT_DIR/scripts/build_cv_content.py"
  } | sort -z | xargs -0 stat -c '%Y %n'
}

watch_pdf() {
  local previous_snapshot current_snapshot

  echo "Watching CV content and LaTeX sources. Press Ctrl+C to stop."
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
