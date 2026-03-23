#!/usr/bin/env bash
set -euo pipefail

echo "[1/3] tectonic main.tex"
tectonic main.tex

echo "[OK] PDF 생성됨: $(pwd)/main.pdf"
ls -lh main.pdf
