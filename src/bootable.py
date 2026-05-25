import os
import urllib.request
import tempfile
import shutil

# For this example, we would normally download a real ISO like Alpine Linux or TinyCore
# and use 'dd' to write it. For simplicity in a Python script, we provide a placeholder URL.
# In a real-world scenario, you might want to package a specific recovery ISO.
ISO_URL = "https://dl-cdn.alpinelinux.org/alpine/v3.18/releases/x86_64/alpine-standard-3.18.4-x86_64.iso"

def download_iso(progress_callback=None, cancel_event=None):
    """
    Downloads a lightweight Linux ISO to a temporary file.
    """
    # Create a secure temporary directory instead of using predictable shared /tmp/recovery_linux.iso
    temp_dir = tempfile.mkdtemp()
    iso_path = os.path.join(temp_dir, "recovery_linux.iso")

    # In a real app we'd cache this more permanently or allow user to select ISO.
    # Since we create a new mkdtemp, we always download here.

    try:
        req = urllib.request.urlopen(ISO_URL)
        total_size = int(req.headers.get('content-length', 0))
        bytes_read = 0
        chunk_size = 8192

        with open(iso_path, 'wb') as f:
            while True:
                if cancel_event and cancel_event.is_set():
                    return False, "Canceled"

                chunk = req.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                bytes_read += len(chunk)

                if progress_callback:
                    progress_callback(bytes_read, total_size)

        return True, iso_path
    except Exception as e:
        return False, str(e)


def write_iso_to_usb(iso_path, usb_device, progress_callback=None, cancel_event=None):
    """
    Writes the ISO file block-by-block to the USB device.
    WARNING: This will overwrite the device.
    """
    try:
        # Get ISO size
        total_size = os.path.getsize(iso_path)
        bytes_read = 0
        block_size = 1024 * 1024 # 1MB blocks

        with open(iso_path, 'rb') as src, open(usb_device, 'wb') as dst:
            while True:
                if cancel_event and cancel_event.is_set():
                    return False, "Canceled"

                chunk = src.read(block_size)
                if not chunk:
                    break
                dst.write(chunk)
                bytes_read += len(chunk)

                if progress_callback:
                    progress_callback(bytes_read, total_size)

        # Flush buffers
        os.sync()
        return True, "Successfully written ISO to USB."
    except Exception as e:
        return False, f"Failed to write to USB: {e}. Note: You may need to run this as root/Administrator."

def create_bootable_usb(usb_device, progress_callback=None, cancel_event=None):
    """
    High-level function to download ISO and write to USB.
    """
    def dl_prog(read, total):
        if progress_callback:
            # Scale download to 0-50%
            pct = (read / total) * 50 if total else 0
            progress_callback(f"Downloading ISO...", pct)

    def write_prog(read, total):
        if progress_callback:
            # Scale write to 50-100%
            pct = 50 + ((read / total) * 50) if total else 50
            progress_callback(f"Writing to {usb_device}...", pct)

    success, result = download_iso(progress_callback=dl_prog, cancel_event=cancel_event)
    if not success:
        return False, f"Download failed: {result}"

    iso_path = result

    success, msg = write_iso_to_usb(iso_path, usb_device, progress_callback=write_prog, cancel_event=cancel_event)

    # Cleanup temp directory
    try:
        shutil.rmtree(os.path.dirname(iso_path))
    except Exception:
        pass

    if not success:
        return False, msg

    return True, "Successfully written ISO to USB. Note: You will need to manually copy the application folder to the USB or another drive to run it after booting."
