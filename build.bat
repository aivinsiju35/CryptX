@echo off
echo ============================================
echo   CryptX - Build Standalone .exe
echo ============================================
echo.

echo [1/3] Installing dependencies...
pip install customtkinter pyinstaller --quiet
if errorlevel 1 (
    echo ERROR: pip install failed. Make sure Python and pip are available.
    pause
    exit /b 1
)

echo [2/3] Building executable with PyInstaller...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "CryptX" ^
    --add-data "caesar.py;." ^
    --add-data "vigenere.py;." ^
    --add-data "frequency_analysis.py;." ^
    --add-data "password_tool.py;." ^
    --add-data "utils.py;." ^
    --hidden-import customtkinter ^
    --hidden-import tkinter ^
    app.py

if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    pause
    exit /b 1
)

echo.
echo [3/3] Done!
echo ============================================
echo   Your executable is in:  dist\CryptX.exe
echo   Double-click it to launch — no Python needed!
echo ============================================
echo.
pause
