param(
    [string]$PythonExe = ".\\.venv\\Scripts\\python.exe"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Write-Host "Using Python:" $PythonExe
& $PythonExe -m PyInstaller --noconfirm --clean PyUCoMX.spec

Write-Host ""
Write-Host "Build complete."
Write-Host "Executable:" (Join-Path $projectRoot "dist\\PyUCoMX.exe")
