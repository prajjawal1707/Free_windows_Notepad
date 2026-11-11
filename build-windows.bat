@echo off
setlocal
cd /d "%~dp0"
echo === Building My Desktop App installer for Windows ===
echo.

echo [1/5] Checking tools...
where node >nul 2>nul
if errorlevel 1 goto nonode
where python >nul 2>nul
if errorlevel 1 goto nopython
where rustc >nul 2>nul
if errorlevel 1 goto norust
where cargo >nul 2>nul
if errorlevel 1 goto norust
echo     Node, Python and Rust found.
echo.

echo [2/5] Installing dependencies (a few minutes)...
call npm install
if errorlevel 1 goto fail
call npm install --prefix frontend
if errorlevel 1 goto fail
python -m pip install -r backend\requirements-dev.txt
if errorlevel 1 goto fail
echo.

echo [3/5] Packaging the Python backend...
python scripts\build-backend.py
if errorlevel 1 goto fail
echo.

echo [4/5] Building the app and installer (first time takes 5-15 minutes, be patient)...
call npx tauri build
if errorlevel 1 goto fail
echo.

echo [5/5] DONE. Your installer:
dir /b src-tauri\target\release\bundle\nsis\*.exe
start "" "src-tauri\target\release\bundle\nsis"
pause
exit /b 0

:nonode
echo ERROR: Node.js not found. Install it from nodejs.org, then run this again.
pause
exit /b 1
:nopython
echo ERROR: Python not found. Install it from python.org and tick Add Python to PATH.
pause
exit /b 1
:norust
echo ERROR: Rust not found. Install it from rustup.rs, then restart and run this again.
pause
exit /b 1
:fail
echo.
echo ERROR: The build failed. Read the messages above to see which step broke.
pause
exit /b 1
