#!/usr/bin/env bash
set -euo pipefail

echo "[1/2] tectonic main.tex (first pass)"
tectonic --keep-intermediates main.tex

echo "[2/2] tectonic main.tex (second pass for cross-references)"
tectonic --keep-intermediates main.tex

echo "[OK] PDF 생성됨: $(pwd)/main.pdf"
ls -lh main.pdf
