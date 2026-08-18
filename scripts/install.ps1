param(
    [switch]$NoPath
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot ".."))
Set-Location $repoRoot

$pythonLauncher = Get-Command py -ErrorAction SilentlyContinue
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($pythonLauncher) {
    & $pythonLauncher.Source -m venv .venv
} elseif ($pythonCommand) {
    & $pythonCommand.Source -m venv .venv
} else {
    throw "Python 3.10+ was not found. Install it from https://www.python.org/downloads/windows/ and enable Add python.exe to PATH."
}

$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
$venvBeton = Join-Path $repoRoot ".venv\Scripts\beton.exe"
& $venvPython -m pip install -e ".[dev]"

$shimDirectory = Join-Path $HOME "bin"
$shimPath = Join-Path $shimDirectory "beton.cmd"
if (-not $NoPath) {
    New-Item -ItemType Directory -Force -Path $shimDirectory | Out-Null
    $shim = "@echo off`r`n`"$venvBeton`" %*`r`n"
    Set-Content -Path $shimPath -Value $shim -Encoding ASCII

    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $pathEntries = @($userPath -split ";" | Where-Object { $_ })
    if ($pathEntries -notcontains $shimDirectory) {
        $newUserPath = (($pathEntries + $shimDirectory) -join ";")
        [Environment]::SetEnvironmentVariable("Path", $newUserPath, "User")
    }
}

Write-Host ""
Write-Host "BETON is installed from the local source checkout."
Write-Host ""
if ($NoPath) {
    Write-Host "Run: .\.venv\Scripts\beton.exe doctor"
} else {
    Write-Host "A user-level beton command shim was created at: $shimPath"
    Write-Host "Open a new VS Code or PowerShell terminal, then run: beton doctor"
    Write-Host "For the current terminal, run: .\.venv\Scripts\beton.exe doctor"
}
