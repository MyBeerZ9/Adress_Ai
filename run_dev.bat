@echo off
title AddressAI Full-Stack Development Launcher
echo ========================================================
echo        AddressAI - Indian Address Parser & Geocoder
echo ========================================================
echo.

echo Starting FastAPI Backend on http://localhost:8000 ...
start "AddressAI Backend (FastAPI)" cmd /k "py -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

echo Starting React (Vite) Frontend on http://localhost:5173 ...
start "AddressAI Frontend (React/Vite)" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers are starting up!
echo - Frontend: http://localhost:5173
echo - Backend API: http://localhost:8000
echo - Swagger Docs: http://localhost:8000/docs
echo ========================================================
pause
