@echo off
setlocal
cd /d "%~dp0"
echo === ebabil kurulumu ===

where git >nul 2>nul || (
    echo Git bulunamadi. Kurmak icin: winget install Git.Git
    exit /b 1
)

rem Once denenmis surumler (en iyi bilinen once), yoksa kurulu en yeni Python 3.11+.
set "PY="
for %%v in (3.13 3.12 3.14 3.11) do (
    if not defined PY ( py -%%v --version >nul 2>nul && set "PY=py -%%v" )
)
if not defined PY (
    for %%c in ("py -3" "python") do (
        if not defined PY (
            %%~c -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul && set "PY=%%~c"
        )
    )
    if defined PY echo Uyari: denenmemis bir Python surumu kullaniliyor. Sorun cikarsa Python 3.13 kurun.
)
if not defined PY (
    echo Python 3.11 ya da daha yenisi bulunamadi.
    echo https://www.python.org/downloads/ adresinden Python 3.13 kurun.
    exit /b 1
)
for /f "delims=" %%s in ('%PY% --version') do echo Python: %%s  [%PY%]

if not exist ".venv\Scripts\python.exe" %PY% -m venv .venv || exit /b 1
".venv\Scripts\python.exe" -m pip install --upgrade pip || exit /b 1
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Paketler kurulamadi. Bu Python surumu icin PyTorch henuz yayinlanmamis olabilir.
    echo Python 3.13 kurup .venv klasorunu silin ve kur.bat'i yeniden calistirin.
    exit /b 1
)

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
