# Build GeoShield.exe (no terminal window when launched)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Installing dependencies..."
python -m pip install -r requirements.txt

Write-Host "Building executable..."
python -m PyInstaller --noconfirm geoshield.spec

$exe = Join-Path $PSScriptRoot "dist\GeoShield.exe"
if (Test-Path $exe) {
    Write-Host ""
    Write-Host "Done: $exe"
    Write-Host "Copy GeoShield.exe anywhere; it will create a 'data' folder next to it for accounts and history."
} else {
    Write-Error "Build failed — GeoShield.exe was not created."
}
