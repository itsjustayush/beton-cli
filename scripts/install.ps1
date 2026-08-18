$ErrorActionPreference = "Stop"

$pythonLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($pythonLauncher) {
    & $pythonLauncher.Source -m venv .venv
} else {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        throw "Python 3.10+ was not found. Install it from https://www.python.org/downloads/windows/ and enable Add python.exe to PATH."
    }
    & $pythonCommand.Source -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
Write-Host ""
Write-Host "BETON is installed. Try: .\.venv\Scripts\beton.exe doctor"
Write-Host "To activate later, use .\.venv\Scripts\Activate.ps1 if your PowerShell policy allows it."
