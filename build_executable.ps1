# Build Pro Ruler Executable
# This script creates a standalone .exe file that runs without Python

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Pro Ruler - Executable Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment if it exists
$venvPath = ".\\.venv\\Scripts\\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & $venvPath
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "No virtual environment found, using system Python..." -ForegroundColor Yellow
}

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "ERROR: Python is not installed!" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Red
    pause
    exit 1
}

$pythonVersion = python --version
Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "✓ PyInstaller installed successfully" -ForegroundColor Green
Write-Host ""

# Build executable
Write-Host "Building executable... (This may take a few minutes)" -ForegroundColor Yellow
python -m PyInstaller ProRuler.spec --clean

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Build Completed Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your executable is ready at:" -ForegroundColor Cyan
Write-Host "  .\dist\ProRuler.exe" -ForegroundColor White
Write-Host ""
Write-Host "You can now:" -ForegroundColor Yellow
Write-Host "  1. Run ProRuler.exe directly" -ForegroundColor White
Write-Host "  2. Copy it to any Windows PC (no Python needed)" -ForegroundColor White
Write-Host "  3. Create a desktop shortcut" -ForegroundColor White
Write-Host ""

# Ask if user wants to run the app
$response = Read-Host "Would you like to run ProRuler.exe now? (Y/N)"
if ($response -eq "Y" -or $response -eq "y") {
    Write-Host "Starting ProRuler..." -ForegroundColor Green
    Start-Process ".\dist\ProRuler.exe"
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
pause
