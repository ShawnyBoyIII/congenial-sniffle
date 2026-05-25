import platform
import subprocess

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

def get_drives():
    """
    Returns a list of dictionaries representing available drives/partitions.
    Format: [{'device': '/dev/sdb', 'description': '14.5 GB'}, ...]
    Attempts to use psutil, and falls back/augments with system commands to ensure
    unmounted physical drives are detected.
    """
    drives = []
    seen_devices = set()

    # Strategy 1: psutil (mostly good for mounted partitions)
    if HAS_PSUTIL:
        try:
            partitions = psutil.disk_partitions(all=False)
            for p in partitions:
                # On Windows, device is 'C:\\'. We'll adjust it later.
                if p.device not in seen_devices:
                    try:
                        usage = psutil.disk_usage(p.mountpoint)
                        total_gb = usage.total / (1024 ** 3)
                        desc = f"{p.device} ({total_gb:.1f} GB) - {p.fstype}"
                        drives.append({"device": p.device, "description": desc})
                        seen_devices.add(p.device)
                    except Exception:
                        pass
        except Exception:
            pass

    sys_plat = platform.system()

    # Strategy 2: System commands to find raw physical drives
    # psutil often misses broken/unmounted drives, which are exactly what we need.
    if sys_plat == "Windows":
        try:
            # wmic diskdrive get name,size,model /format:csv
            cmd = ['wmic', 'diskdrive', 'get', 'name,size,model', '/format:csv']
            output = subprocess.check_output(cmd, creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0).decode('utf-8', errors='ignore')
            lines = output.strip().split('\\n')
            for line in lines[1:]: # Skip header
                parts = line.strip().split(',')
                if len(parts) >= 4:
                    # Node, Model, Name, Size
                    model = parts[1].strip()
                    name = parts[2].strip() # e.g., \\\\.\\PHYSICALDRIVE1
                    size_bytes = parts[3].strip()

                    if name and size_bytes.isdigit():
                        if name not in seen_devices:
                            size_gb = int(size_bytes) / (1024 ** 3)
                            desc = f"{name} ({size_gb:.1f} GB) - {model}"
                            drives.append({"device": name, "description": desc})
                            seen_devices.add(name)
        except Exception:
            pass

    elif sys_plat == "Linux":
        try:
            # lsblk -b -P -o NAME,SIZE,MODEL,TYPE
            cmd = ['lsblk', '-b', '-P', '-o', 'NAME,SIZE,MODEL,TYPE']
            output = subprocess.check_output(cmd).decode('utf-8', errors='ignore')
            for line in output.strip().split('\\n'):
                # NAME="sda" SIZE="500107862016" MODEL="Samsung SSD 850 " TYPE="disk"
                data = {}
                for token in line.split('" '):
                    if '=' in token:
                        k, v = token.split('=', 1)
                        data[k.strip().replace('"', '')] = v.strip().replace('"', '')

                if data.get('TYPE') == 'disk' or data.get('TYPE') == 'part':
                    name = "/dev/" + data.get('NAME', '')
                    if name and name not in seen_devices:
                        size_bytes = data.get('SIZE', '0')
                        model = data.get('MODEL', 'Unknown Device')
                        if size_bytes.isdigit():
                            size_gb = int(size_bytes) / (1024 ** 3)
                            desc = f"{name} ({size_gb:.1f} GB) - {model}"
                            drives.append({"device": name, "description": desc})
                            seen_devices.add(name)
        except Exception:
            pass

    elif sys_plat == "Darwin": # macOS
        try:
            # diskutil list -plist could be parsed, or simple awk
            # Fallback simple parsing for macOS can be complex, adding basic placeholder
            pass
        except Exception:
            pass

    # If everything fails, return at least an empty list or some basic info
    return drives

def get_drive_descriptions():
    """Returns a list of description strings for the UI."""
    return [d['description'] for d in get_drives()]

def get_device_path(description):
    """Parses the device path back out from the description string."""
    drives = get_drives()
    for d in drives:
        if d['description'] == description:
            return d['device']

    # Fallback if user manually typed something
    return description.split(' ')[0] if description else ""

if __name__ == "__main__":
    print("Detected Drives:")
    for d in get_drives():
        print(f" - {d['description']}")
