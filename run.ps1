# PowerShell Shortcut Runner for Smart Event Ticketing System
param (
    [string]$Action = "server"
)

$VenvPython = ".\.venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "[!] Virtual environment not found. Please run 'python -m venv .venv' and install requirements." -ForegroundColor Red
    exit 1
}

switch ($Action.ToLower()) {
    "server" {
        Write-Host "[*] Starting Smart Event Ticketing Server on http://127.0.0.1:8000 ..." -ForegroundColor Cyan
        & $VenvPython -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
    }
    "test" {
        Write-Host "[*] Running automated test suite with pytest..." -ForegroundColor Cyan
        & $VenvPython -m pytest tests -v
    }
    "experiment" {
        Write-Host "[*] Running HOG-KNN vs PSO-KNN research benchmark experiment..." -ForegroundColor Cyan
        & $VenvPython -m research.experiments.run_experiment
    }
    "migrate" {
        Write-Host "[*] Running Alembic database migrations..." -ForegroundColor Cyan
        & $VenvPython -m alembic upgrade head
    }
    default {
        Write-Host "Usage: .\run.ps1 [server | test | experiment | migrate]" -ForegroundColor Yellow
    }
}

