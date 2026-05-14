#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LATEX_DIR="$ROOT_DIR/assets/latex"
OUTPUT_PDF="$ROOT_DIR/assets/pdf/ZhaominWu.pdf"

if ! command -v make >/dev/null 2>&1; then
  echo "Error: make is not installed or not on PATH." >&2
  exit 127
fi

if ! command -v pdflatex >/dev/null 2>&1; then
  echo "Error: pdflatex is not installed or not on PATH." >&2
  exit 127
fi

make -B -C "$LATEX_DIR" "$@"

if [[ -f "$OUTPUT_PDF" ]]; then
  echo "Built: $OUTPUT_PDF"
fi
