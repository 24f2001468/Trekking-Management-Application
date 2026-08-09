# =====================================================
# TMA - Start All Services
# Run from project root: .\start.ps1
# =====================================================

$projectRoot  = $PSScriptRoot
$backendPath  = Join-Path $projectRoot "backend"
$frontendPath = Join-Path $projectRoot "frontend"
$venvPython   = Join-Path $projectRoot "venv\Scripts\python.exe"
$activateCmd  = Join-Path $projectRoot "venv\Scripts\Activate.ps1"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Trekking Management App...  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Redis via Docker
Write-Host "[1/5] Starting Redis (Docker)..." -ForegroundColor Yellow
try {
    $redisRunning = docker ps --filter "ancestor=redis" --format "{{.ID}}" 2>$null
    if ($redisRunning) {
        Write-Host "      Redis already running. Skipping." -ForegroundColor Green
    } else {
        docker run -d -p 6379:6379 redis | Out-Null
        Write-Host "      Redis started on localhost:6379" -ForegroundColor Green
    }
} catch {
    Write-Host "      WARNING: Docker not found. Celery features will not work." -ForegroundColor Red
}

Start-Sleep -Seconds 1

# 2. Initialize DB on first run
Write-Host "[2/5] Checking database..." -ForegroundColor Yellow
$dbFile = Join-Path $backendPath "tma.sqlite3"
if (-not (Test-Path $dbFile)) {
    Write-Host "      First run - initialising database..." -ForegroundColor Cyan
    & $venvPython (Join-Path $backendPath "init_db.py")
    Write-Host "      Done. Login: admin / admin123" -ForegroundColor Green
} else {
    Write-Host "      Database found. Skipping init." -ForegroundColor Green
}

# 3. Flask Backend
Write-Host "[3/5] Starting Flask Backend..." -ForegroundColor Yellow
$flaskCmd = "& '" + $activateCmd + "'; cd '" + $backendPath + "'; python app.py"
Start-Process "powershell" -ArgumentList "-NoExit", "-Command", $flaskCmd

Start-Sleep -Seconds 2

# 4. Celery Worker (required for CSV export and batch jobs)
Write-Host "[4/5] Starting Celery Worker..." -ForegroundColor Yellow
$celeryWorkerCmd = "& '" + $activateCmd + "'; cd '" + $backendPath + "'; celery -A celery_worker.celery_instance worker --pool=solo -l info"
Start-Process "powershell" -ArgumentList "-NoExit", "-Command", $celeryWorkerCmd

# 5. Celery Beat (required for scheduled daily reminders + monthly reports)
Write-Host "[5/5] Starting Celery Beat..." -ForegroundColor Yellow
$celeryBeatCmd = "& '" + $activateCmd + "'; cd '" + $backendPath + "'; celery -A celery_worker.celery_instance beat -l info"
Start-Process "powershell" -ArgumentList "-NoExit", "-Command", $celeryBeatCmd

# 6. Vue Frontend
Write-Host "[6/6] Starting Vue Frontend..." -ForegroundColor Yellow
$frontendCmd = "cd '" + $frontendPath + "'; npm run dev"
Start-Process "powershell" -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  All services started!" -ForegroundColor Green
Write-Host ""
Write-Host "  Open in browser: http://localhost:5173" -ForegroundColor White
Write-Host "  Flask API:       http://localhost:5000" -ForegroundColor White
Write-Host "  Redis:           localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "  Default login:   admin / admin123" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
