import os

# Define file signatures: (Header, Footer, Extension)
# Note: For many formats, the footer is not always reliable or present.
# We will define some common ones, and if no footer is known, we extract a maximum size.
SIGNATURES = [
    {
        'ext': 'jpg',
        'header': b'\xff\xd8\xff',
        'footer': b'\xff\xd9',
        'max_size': 10 * 1024 * 1024 # 10MB max if no footer found
    },
    {
        'ext': 'png',
        'header': b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a',
        'footer': b'\x49\x45\x4e\x44\xae\x42\x60\x82',
        'max_size': 10 * 1024 * 1024
    },
    {
        'ext': 'pdf',
        'header': b'%PDF-',
        'footer': b'%%EOF',
        'max_size': 20 * 1024 * 1024
    },
    {
        'ext': 'mp4',
        'header': b'\x00\x00\x00\x18ftypmp42',
        'footer': None,
        'max_size': 500 * 1024 * 1024 # 500MB max
    },
    {
        'ext': 'mp4', # Alternative MP4 header
        'header': b'\x00\x00\x00\x20ftypisom',
        'footer': None,
        'max_size': 500 * 1024 * 1024
    },
    {
        'ext': 'docx', # Or zip/xlsx etc.
        'header': b'PK\x03\x04',
        'footer': b'PK\x05\x06', # End of central directory record (rough approximation)
        'max_size': 50 * 1024 * 1024
    }
]

def carve_files(source_path, output_dir, progress_callback=None, cancel_event=None):
    """
    Scans the source_path for file signatures and extracts them to output_dir.

    :param source_path: The raw .img file or block device to scan.
    :param output_dir: Directory to save the recovered files.
    :param progress_callback: Function to call with progress updates: cb(bytes_read, total_bytes, files_found)
    :param cancel_event: A threading.Event to check if the user canceled the operation.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        if os.path.isfile(source_path):
            total_size = os.path.getsize(source_path)
        else:
            try:
                fd = os.open(source_path, os.O_RDONLY)
                total_size = os.lseek(fd, 0, os.SEEK_END)
                os.close(fd)
            except Exception:
                total_size = 0
    except Exception:
        total_size = 0

    files_found = 0
    bytes_read = 0
    chunk_size = 1024 * 1024 * 4 # 4MB chunk size for reading

    # We read in chunks, but headers might cross chunk boundaries.
    # A robust carver needs a sliding window or overlap.
    # For simplicity, we use an overlap equal to the max header length.
    max_header_len = max(len(sig['header']) for sig in SIGNATURES)
    overlap = max_header_len

    with open(source_path, 'rb') as f:
        buffer = b''
        while True:
            if cancel_event and cancel_event.is_set():
                break

            chunk = f.read(chunk_size)
            if not chunk:
                break

            buffer += chunk
            bytes_read += len(chunk)

            # Search for signatures in the buffer
            # We must be careful because we might find multiple files or incomplete files
            found_any = True
            while found_any:
                found_any = False
                earliest_idx = -1
                best_sig = None

                # Find the earliest header in the buffer
                for sig in SIGNATURES:
                    idx = buffer.find(sig['header'])
                    if idx != -1:
                        if earliest_idx == -1 or idx < earliest_idx:
                            earliest_idx = idx
                            best_sig = sig

                if best_sig and earliest_idx != -1:
                    found_any = True
                    # We found a header. We need to extract the file.
                    # Does the buffer contain the footer, or the max_size?
                    start_idx = earliest_idx
                    end_idx = -1

                    if best_sig['footer']:
                        # Look for footer after header
                        footer_idx = buffer.find(best_sig['footer'], start_idx + len(best_sig['header']))
                        if footer_idx != -1:
                            end_idx = footer_idx + len(best_sig['footer'])

                    if end_idx == -1:
                        # No footer found in this buffer.
                        # Is the buffer large enough to contain max_size from the start_idx?
                        if len(buffer) - start_idx >= best_sig['max_size']:
                            end_idx = start_idx + best_sig['max_size']
                        elif not chunk:
                            # EOF reached, take what's left
                            end_idx = len(buffer)

                    if end_idx != -1:
                        # We have the bounds of the file!
                        file_data = buffer[start_idx:end_idx]

                        # Save the file
                        files_found += 1
                        out_path = os.path.join(output_dir, f"recovered_{files_found}.{best_sig['ext']}")
                        with open(out_path, 'wb') as out_f:
                            out_f.write(file_data)

                        # Remove the processed part from the buffer
                        buffer = buffer[end_idx:]
                    else:
                        # We have a header but not the end of the file.
                        # We must read more data into the buffer. Break the inner loop.
                        found_any = False

            # Keep only the last part of the buffer to handle cross-chunk headers
            # ONLY if we aren't currently trying to accumulate a large file
            # If we have a pending header at the start of the buffer, we MUST NOT truncate it.
            # Check if there's any header in the current buffer.
            has_header = False
            for sig in SIGNATURES:
                if sig['header'] in buffer:
                    has_header = True
                    break

            if not has_header:
                # Safe to truncate
                if len(buffer) > overlap:
                    buffer = buffer[-overlap:]
            else:
                # If buffer gets too large (e.g. larger than any max_size), force a truncate to avoid OOM
                max_possible_size = max(sig['max_size'] for sig in SIGNATURES)
                if len(buffer) > max_possible_size * 2:
                    buffer = buffer[-overlap:]

            if progress_callback:
                progress_callback(bytes_read, total_size, files_found)

    return True, f"Carving complete. Found {files_found} files."
