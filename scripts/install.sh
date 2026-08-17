#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
printf '\nBETON is installed. Try: beton doctor\n'
