@echo off
setlocal
cd /d "%~dp0"
echo === ebabil kurulumu ===

where git >nul 2>nul || (
    echo Git bulunamadi. Kurmak icin: winget install Git.Git
    exit /b 1
)

set "PY="
for %%v in (3.13 3.12 3.11) do (
    if not defined PY ( py -%%v --version >nul 2>nul && set "PY=py -%%v" )
)
if not defined PY (
    echo Python 3.11-3.13 bulunamadi. https://www.python.org/downloads/ adresinden kurun.
    exit /b 1
)
echo Python: %PY%

if not exist ".venv\Scripts\python.exe" %PY% -m venv .venv || exit /b 1
".venv\Scripts\python.exe" -m pip install --upgrade pip || exit /b 1
".venv\Scripts\python.exe" -m pip install -r requirements.txt || exit /b 1

where ffmpeg >nul 2>nul
if errorlevel 1 if not exist "%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe" (
    echo ffmpeg kuruluyor...
    winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
)

echo Ses modeli indiriliyor...
".venv\Scripts\python.exe" -c "import sys; sys.path.insert(0, '.'); from ses import model_yukle; model_yukle()" || exit /b 1

echo.
echo Kurulum tamam. Kullanim: ebabil.bat ses dosya.srt
echo Her klasorden "ebabil" yazabilmek icin bu klasoru PATH'e ekleyin:
echo   %~dp0
