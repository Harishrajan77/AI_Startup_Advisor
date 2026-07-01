@echo off
title AI Startup Advisor Runner
setlocal enabledelayedexpansion

:: Set colors if supported, or use clean formatting
cls
echo =====================================================================
echo    ___  ___   ____  _                 _                _             
echo   / _ \/ _ \ / ___^| ^|_ __ _ _ __ ^| ^|_ _   _ _ __   / \   _  __   __ 
echo  / /_\/ /_\ \___ \^| __/ _` ^| '__^| __^| ^| ^| ^| '_ \ / _ \ ^| ^| \ \ / / 
echo / /_\\/ /_\\ ___) ^| ^|_^| (_^| ^| ^|  ^| ^|_^| ^|_^| ^| ^|_) / ___ \^| ^|  \ V /  
echo \____/\____/^|____/ \__\__,_^|_^|   \__^|\__,_^| .__/_/   \_\_^|   \_/   
echo                                           ^|_^|                      
echo =====================================================================
echo                     AI STARTUP VALIDATION ENGINE                      
echo =====================================================================
echo.

:: 1. Sync .env configuration if root .env has no key but backend/.env does
if not exist .env (
    if exist backend\.env (
        echo [INFO] Copying environment configuration from backend\.env to root...
        copy backend\.env .env > nul
    ) else (
        echo [WARNING] No .env file found. Please create a .env file based on .env.example.
    )
) else (
    :: Check if GROQ_API_KEY is empty in root .env but set in backend/.env
    findstr /C:"GROQ_API_KEY=gsk" .env > nul
    if errorlevel 1 (
        if exist backend\.env (
            findstr /C:"GROQ_API_KEY=gsk" backend\.env > nul
            if not errorlevel 1 (
                echo [INFO] Synchronizing GROQ_API_KEY from backend\.env to root .env for Docker...
                copy /y backend\.env .env > nul
            )
        )
    )
)

:menu
echo Select how you want to run the application:
echo.
echo   [1] Run with Docker Compose (Recommended - Starts Postgres, Backend, Frontend)
echo   [2] Run Locally (Uses SQLite, Backend and Frontend run in separate local windows)
echo   [3] Check Prerequisites (Docker, Python, Node.js)
echo   [4] Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto run_docker
if "%choice%"=="2" goto run_local
if "%choice%"=="3" goto check_prereqs
if "%choice%"=="4" exit
echo Invalid choice. Please try again.
echo.
goto menu

:run_docker
echo.
echo =====================================================================
echo Starting application with Docker Compose...
echo =====================================================================
echo Checking if Docker is running...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running or not installed. 
    echo Please make sure Docker Desktop is started and try again.
    echo.
    pause
    goto menu
)
echo Starting containers...
docker-compose up --build
goto end

:run_local
echo.
echo =====================================================================
echo Starting application locally...
echo =====================================================================

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.9+ and try again.
    echo.
    pause
    goto menu
)

:: Check Node/NPM
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js/NPM is not installed or not in your PATH.
    echo Please install Node.js and try again.
    echo.
    pause
    goto menu
)

:: Setup Backend
echo Setting up Python virtual environment...
if not exist backend\venv (
    echo Creating virtual environment in backend/venv...
    cd backend
    python -m venv venv
    cd ..
)

echo Activating virtual environment and installing backend dependencies...
cd backend
call venv\Scripts\activate.bat
pip install -r requirements.txt
cd ..

:: Setup Frontend
echo Setting up frontend dependencies...
if not exist frontend\node_modules (
    echo Installing npm dependencies in frontend...
    cd frontend
    call npm install
    cd ..
)

:: Start Backend in a new window
echo Starting Backend API Server...
start "AI Startup Advisor - Backend API" cmd /k "title AI Startup Advisor Backend && cd backend && call venv\Scripts\activate.bat && python -m app.main"

:: Start Frontend in a new window
echo Starting Frontend Development Server...
start "AI Startup Advisor - Frontend Dashboard" cmd /k "title AI Startup Advisor Frontend && cd frontend && call npm run dev"

echo.
echo =====================================================================
echo Application servers are launching!
echo.
echo   - Frontend: http://localhost:5173
echo   - Backend API: http://localhost:8000
echo   - API Documentation: http://localhost:8000/docs
echo =====================================================================
echo.
echo Opening default web browser in 5 seconds...
timeout /t 5 > nul
start http://localhost:5173
goto end

:check_prereqs
echo.
echo =====================================================================
echo Checking Prerequisites...
echo =====================================================================
echo.

where docker >nul 2>&1
if %errorlevel% eq 0 (
    echo [OK] Docker is installed.
    docker --version
) else (
    echo [MISSING] Docker is not installed. (Required for Docker Compose mode)
)
echo.

where python >nul 2>&1
if %errorlevel% eq 0 (
    echo [OK] Python is installed.
    python --version
) else (
    echo [MISSING] Python is not installed. (Required for local mode)
)
echo.

where npm >nul 2>&1
if %errorlevel% eq 0 (
    echo [OK] Node.js/NPM is installed.
    echo npm version:
    call npm -v
) else (
    echo [MISSING] Node.js/NPM is not installed. (Required for local mode)
)
echo.
pause
cls
goto menu

:end
pause
