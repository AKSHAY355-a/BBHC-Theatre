@echo off
echo ============================================================
echo   BBHC Theatre - Starting All Services
echo ============================================================
echo.
echo Starting Backend Server (Port 5000)...
start "BBHC Backend" cmd /k "cd /d "%~dp0backend" && python main.py"

timeout /t 3 /nobreak > nul

echo Starting Streaming Server (Port 8080)...
start "Redmoon Streamer" cmd /k "cd /d "%~dp0redmoon-stream-master" && python telegram_video_streamer.py"

timeout /t 2 /nobreak > nul

echo.
echo ============================================================
echo   All services started!
echo   - Backend API: http://localhost:5000
echo   - Streaming: http://localhost:8080
echo   - Frontend: Open index.html in browser
echo ============================================================
echo.
echo Press any key to stop all services...
pause > nul

taskkill /FI "WindowTitle eq BBHC Backend*" /T /F
taskkill /FI "WindowTitle eq Redmoon Streamer*" /T /F
