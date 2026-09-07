<#
Install dependencies for the femap-api-python repository (Windows PowerShell).

Usage (PowerShell):
  .\scripts\install_deps.ps1

This script will:
- locate Python from PATH
- create a virtual environment at `venv/` if missing
- upgrade pip and install packages from `requirements.txt`

Notes:
- `pyfemap` is typically provided by the Femap installation (not always on PyPI).
#>

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..")
$venvPath = Join-Path $RepoRoot "venv"
$reqFile = Join-Path $RepoRoot "requirements.txt"

Write-Host "Repository root: $RepoRoot"

# Find python
$pythonCmd = (Get-Command python -ErrorAction SilentlyContinue).Path
if (-not $pythonCmd) {
    Write-Error "Python not found in PATH. Please install Python 3.8+ and re-run."
    exit 1
}

if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at: $venvPath"
    & $pythonCmd -m venv $venvPath
}

$python = Join-Path $venvPath "Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Error "Python executable not found in virtual environment. venv creation may have failed."
    exit 1
}

Write-Host "Upgrading pip..."
& $python -m pip install --upgrade pip

if (-not (Test-Path $reqFile)) {
    Write-Warning "requirements.txt not found at $reqFile. Nothing to install."
    exit 0
}

Write-Host "Installing packages from requirements.txt..."
try {
    & $python -m pip install -r $reqFile
} catch {
    Write-Warning "pip install reported an error."
    Write-Warning "If the failure mentions 'pyfemap', note that 'pyfemap' is often provided by the Femap application/SDK and may not be installable via pip."
    Write-Warning "You can remove 'pyfemap' from requirements.txt and re-run this script, or install pyfemap via the Femap SDK as instructed by your Femap installation." 
    exit 0
}

Write-Host "Dependencies installed. To activate the venv, run:`n`n  .\venv\Scripts\Activate.ps1`n"
