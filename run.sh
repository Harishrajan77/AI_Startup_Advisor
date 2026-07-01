#!/bin/bash

# Clear terminal screen
clear

echo "====================================================================="
echo "   ___  ___   ____  _                 _                _             "
echo "  / _ \/ _ \ / ___| | |_ __ _ _ __ | |_ _   _ _ __   / \   _  __   __ "
echo " / /_\/ /_\ \___ \| __/ _\` | '_ \| __| | | | '_ \ / _ \ | | \ \ / / "
echo "/ /_\\\/ /_\\\ ___) | |_| (_| | |  | |_| |_| | |_) / ___ \| |  \ V /  "
echo "\____/\____/|____/ \__\__,_|_|   \__|\__,_| .__/_/   \_\_|   \_/   "
echo "                                          |_|                      "
echo "====================================================================="
echo "                    AI STARTUP VALIDATION ENGINE                      "
echo "====================================================================="
echo

# 1. Sync .env configuration if root .env has no key but backend/.env does
if [ ! -f .env ]; then
    if [ -f backend/.env ]; then
        echo "[INFO] Copying environment configuration from backend/.env to root..."
        cp backend/.env .env
    else
        echo "[WARNING] No .env file found. Please create a .env file based on .env.example."
    fi
else
    # Check if GROQ_API_KEY is empty in root .env but set in backend/.env
    if ! grep -q "GROQ_API_KEY=gsk" .env; then
        if [ -f backend/.env ] && grep -q "GROQ_API_KEY=gsk" backend/.env; then
            echo "[INFO] Synchronizing GROQ_API_KEY from backend/.env to root .env for Docker..."
            cp backend/.env .env
        fi
    fi
fi

show_menu() {
    echo "Select how you want to run the application:"
    echo
    echo "  [1] Run with Docker Compose (Recommended - Starts Postgres, Backend, Frontend)"
    echo "  [2] Run Locally (Uses SQLite, Backend and Frontend run in separate processes)"
    echo "  [3] Check Prerequisites (Docker, Python, Node.js)"
    echo "  [4] Exit"
    echo
    read -p "Enter your choice (1-4): " choice
    case $choice in
        1) run_docker ;;
        2) run_local ;;
        3) check_prereqs ;;
        4) exit 0 ;;
        *) echo "Invalid choice. Please try again."; echo; show_menu ;;
    esac
}

run_docker() {
    echo
    echo "====================================================================="
    echo "Starting application with Docker Compose..."
    echo "====================================================================="
    if ! command -v docker &> /dev/null; then
        echo "[ERROR] Docker is not installed. Please install Docker and try again."
        echo
        read -p "Press Enter to return to menu..."
        show_menu
        return
    fi
    
    if ! docker info &> /dev/null; then
        echo "[ERROR] Docker daemon is not running. Please start Docker Desktop and try again."
        echo
        read -p "Press Enter to return to menu..."
        show_menu
        return
    fi

    echo "Starting containers..."
    docker-compose up --build
}

run_local() {
    echo
    echo "====================================================================="
    echo "Starting application locally..."
    echo "====================================================================="

    # Check Python
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        echo "[ERROR] Python is not installed. Please install Python 3.9+ and try again."
        echo
        read -p "Press Enter to return to menu..."
        show_menu
        return
    fi

    PYTHON_CMD="python3"
    if ! command -v python3 &> /dev/null; then
        PYTHON_CMD="python"
    fi

    # Check Node/NPM
    if ! command -v npm &> /dev/null; then
        echo "[ERROR] Node.js/NPM is not installed. Please install Node.js and try again."
        echo
        read -p "Press Enter to return to menu..."
        show_menu
        return
    fi

    # Setup Backend Virtual Environment
    echo "Setting up Python virtual environment..."
    if [ ! -d "backend/venv" ]; then
        echo "Creating virtual environment in backend/venv..."
        cd backend
        $PYTHON_CMD -m venv venv
        cd ..
    fi

    echo "Installing backend dependencies..."
    cd backend
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..

    # Setup Frontend node_modules
    echo "Setting up frontend dependencies..."
    if [ ! -d "frontend/node_modules" ]; then
        echo "Installing npm dependencies in frontend..."
        cd frontend
        npm install
        cd ..
    fi

    # Define function to clean up background processes on exit
    cleanup() {
        echo
        echo "Stopping development servers..."
        kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
        exit 0
    }
    trap cleanup SIGINT SIGTERM

    # Start Backend
    echo "Starting Backend API Server..."
    cd backend
    source venv/bin/activate
    python -m app.main &
    BACKEND_PID=$!
    cd ..

    # Start Frontend
    echo "Starting Frontend Development Server..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..

    echo
    echo "====================================================================="
    echo "Application servers are launching!"
    echo
    echo "  - Frontend: http://localhost:5173"
    echo "  - Backend API: http://localhost:8000"
    echo "  - API Documentation: http://localhost:8000/docs"
    echo "====================================================================="
    echo
    echo "Opening default web browser in 5 seconds..."
    sleep 5
    
    # Open browser based on OS
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:5173
    elif command -v open &> /dev/null; then
        open http://localhost:5173
    fi

    # Keep script running to catch Ctrl+C and kill background processes
    wait
}

check_prereqs() {
    echo
    echo "====================================================================="
    echo "Checking Prerequisites..."
    echo "====================================================================="
    echo

    if command -v docker &> /dev/null; then
        echo "[OK] Docker is installed."
        docker --version
    else
        echo "[MISSING] Docker is not installed. (Required for Docker Compose mode)"
    fi
    echo

    if command -v python3 &> /dev/null; then
        echo "[OK] Python is installed."
        python3 --version
    elif command -v python &> /dev/null; then
        echo "[OK] Python is installed."
        python --version
    else
        echo "[MISSING] Python is not installed. (Required for local mode)"
    fi
    echo

    if command -v npm &> /dev/null; then
        echo "[OK] Node.js/NPM is installed."
        echo -n "npm version: "
        npm -v
    else
        echo "[MISSING] Node.js/NPM is not installed. (Required for local mode)"
    fi
    echo
    read -p "Press Enter to return to menu..."
    clear
    show_menu
}

# Run the menu
show_menu
