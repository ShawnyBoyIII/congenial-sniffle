#!/bin/bash
# Build script for Linux/macOS to create a standalone executable

echo "Checking for PyInstaller..."
if ! command -v pyinstaller &> /dev/null
then
    echo "PyInstaller could not be found. Please run 'pip install -r requirements.txt' first."
    exit 1
fi

echo "Building ResQCard standalone binary..."
# --onefile creates a single executable
# --noconsole removes the background terminal window (useful for GUI apps)
# --name sets the output file name
pyinstaller --noconfirm --onedir --windowed --name "ResQCard" src/main.py

echo "Build complete! The executable is located in the 'dist/ResQCard' directory."
echo "You can run it via: sudo ./dist/ResQCard/ResQCard"
