import os

def create_image(source_path, dest_path, block_size=4096, progress_callback=None, cancel_event=None):
    """
    Creates a bit-by-bit image of the source_path to dest_path.
    Ignores read errors by replacing unreadable blocks with zeros.

    :param source_path: The block device or file to read from (e.g. /dev/sdb).
    :param dest_path: The output .img file.
    :param block_size: The size of blocks to read.
    :param progress_callback: Function to call with progress updates: cb(bytes_read, total_bytes, errors)
    :param cancel_event: A threading.Event to check if the user canceled the operation.
    """
    try:
        # Try to get the total size of the device/file.
        # For block devices, os.path.getsize might not work on all systems.
        try:
            total_size = get_device_size(source_path)
        except Exception:
            total_size = 0 # Unknown size

        bytes_read = 0
        errors = 0

        with open(source_path, 'rb') as src, open(dest_path, 'wb') as dst:
            while True:
                if cancel_event and cancel_event.is_set():
                    break

                try:
                    data = src.read(block_size)
                    if not data:
                        break # EOF
                    dst.write(data)

                    bytes_read += len(data)

                except OSError as e:
                    # If we can't read a block, write zeros.
                    errors += 1
                    dst.write(b'\x00' * block_size)
                    bytes_read += block_size
                    # Try to seek past the bad block
                    try:
                        src.seek(bytes_read)
                    except OSError:
                        pass # If we can't seek, we might just fail entirely.

                if progress_callback and (bytes_read % (block_size * 1024) == 0):
                    # Update progress every ~4MB
                    progress_callback(bytes_read, total_size, errors)

        if progress_callback:
            progress_callback(bytes_read, total_size, errors)

        return True, "Imaging complete."
    except Exception as e:
        return False, str(e)


def get_device_size(device_path):
    """Attempt to get the size of a block device or file."""
    # Try getting file size
    if os.path.isfile(device_path):
        return os.path.getsize(device_path)

    # Linux block device
    try:
        fd = os.open(device_path, os.O_RDONLY)
        size = os.lseek(fd, 0, os.SEEK_END)
        os.close(fd)
        return size
    except Exception:
        pass

    return 0
