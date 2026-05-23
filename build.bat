@echo off
REM Build script for Windows to create a standalone executable

echo Checking for PyInstaller...
where pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller could not be found. Please run 'pip install -r requirements.txt' first.
    pause
    exit /b 1
)

echo Building ResQCard standalone executable...
REM --onedir is generally faster and more stable for tkinter apps than --onefile
REM --windowed removes the background command prompt window
REM --name sets the output file name
pyinstaller --noconfirm --onedir --windowed --name "ResQCard" src\main.py

echo Build complete! The executable is located in the 'dist\ResQCard' directory.
pause
