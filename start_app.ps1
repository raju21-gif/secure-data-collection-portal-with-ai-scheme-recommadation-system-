Write-Host "Starting Application Setup..." -ForegroundColor Green

# 1. Install Backend Requirements
Write-Host "Installing Backend Requirements..." -ForegroundColor Yellow
Push-Location "data/backend"
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install requirements. Please check your python installation." -ForegroundColor Red
    Pause
    exit
}
Pop-Location

# 2. Start Backend Server (Unified Backend)
Write-Host "Starting Backend Server..." -ForegroundColor Green
$backendPath = Join-Path $PSScriptRoot "data\backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; uvicorn main:app --reload --port 8000"

# 3. Start Frontend Server
Write-Host "Starting Frontend Server..." -ForegroundColor Green
$frontendPath = $PSScriptRoot
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev -- --force"

Write-Host "Application Started! Check the new windows." -ForegroundColor Cyan
Write-Host "Backend is running on http://127.0.0.1:8000"
Write-Host "Frontend is running on http://localhost:5173"
Pause
