# ResQCard
This application is a GUI-based data extraction tool intended for failing memory cards.
It supports creating a raw image of a device (skipping bad sectors), extracting files via magic byte carving,
and writing a bootable Linux environment to a USB drive containing the app itself.

## Requirements
- Python 3
- Tkinter (usually included with Python)
- Root/Admin privileges (required for reading raw devices and writing USBs)

## Usage
If running from source:
`sudo python3 src/main.py`

## Building Standalone Executables
You can build a standalone executable so that users do not need to install Python to run ResQCard.

**Prerequisites:**
Install the build tools:
`pip install -r requirements.txt`

**For Windows:**
Double-click `build.bat` or run it from a Command Prompt. The standalone application will be generated in the `dist\ResQCard` folder. You can zip this folder and share it. Users just need to run `ResQCard.exe` inside it.

**For Linux/macOS:**
Run `./build.sh` from the terminal. The standalone application will be generated in `dist/ResQCard`. Users can run it via `sudo ./dist/ResQCard/ResQCard`.
