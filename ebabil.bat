@echo off
if not exist "%~dp0.venv\Scripts\python.exe" (
    echo ebabil kurulu degil. Once kur.bat dosyasini calistirin.
    exit /b 1
)
"%~dp0.venv\Scripts\python.exe" "%~dp0ebabil.py" %*
