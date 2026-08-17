$ErrorActionPreference = "Stop"

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Write-Host ""
Write-Host "BETON is installed. Try: beton doctor"
