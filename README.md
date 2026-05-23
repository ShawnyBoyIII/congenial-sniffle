# ResQCard
This application is a GUI-based data extraction tool intended for failing memory cards.
It supports creating a raw image of a device (skipping bad sectors), extracting files via magic byte carving,
and writing a bootable Linux environment to a USB drive containing the app itself.

## Requirements
- Python 3
- Tkinter (usually included with Python)
- Root/Admin privileges (required for reading raw devices and writing USBs)

## Usage
Run `sudo python3 src/main.py`
