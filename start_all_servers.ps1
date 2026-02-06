
Write-Host "--- STARTING ALL SERVERS ---" -ForegroundColor Cyan

# 1. Start Backend (Python Uvicorn)
Write-Host "Starting Backend on Port 8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'backend'; python -m uvicorn app:app --reload --port 8000"

# 2. Wait a bit for backend to initialize
Start-Sleep -Seconds 3

# 3. Start Frontend (Vite)
Write-Host "Starting Frontend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev"

# 4. Start Ngrok (Tunnel)
Write-Host "Starting Ngrok on Port 8000..." -ForegroundColor Green
# Using the path we found earlier
Start-Process powershell -ArgumentList "-NoExit", "-Command", "c:\Users\Maheswari\Downloads\ngrok-v3-stable-windows-amd64\ngrok.exe http 8000"

Write-Host "All servers launched in separate windows!" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: http://localhost:5173"
Write-Host "Ngrok: (Check the Ngrok window for URL)"
