#!/usr/bin/env python3
"""Install Tuna's portable configuration and reload it when Tuna is running."""

import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


source = Path(sys.argv[1])
destination = Path.home() / "Library/Application Support/Tuna/config.toml"
contents = source.read_text().replace("__HOME__", str(Path.home()))

if destination.exists() and destination.read_text() == contents:
    print("Tuna settings already match")
    sys.exit(0)

running = subprocess.run(["pgrep", "-x", "Tuna"], capture_output=True).returncode == 0
tuna = shutil.which("tuna") if running else None
restart = running and tuna is None
if restart:
    subprocess.run(["osascript", "-e", 'tell application "Tuna" to quit'], check=True)
    for _ in range(40):
        if subprocess.run(["pgrep", "-x", "Tuna"], capture_output=True).returncode != 0:
            break
        time.sleep(0.25)
    else:
        raise RuntimeError("Tuna did not quit before installing its settings")

destination.parent.mkdir(parents=True, exist_ok=True)
descriptor, temporary = tempfile.mkstemp(prefix=".config.toml.", dir=destination.parent)
try:
    with os.fdopen(descriptor, "w") as output:
        output.write(contents)
        output.flush()
        os.fsync(output.fileno())
    os.replace(temporary, destination)
finally:
    if os.path.exists(temporary):
        os.unlink(temporary)

if restart:
    subprocess.run(["open", "-a", "Tuna"], check=True)
    for _ in range(40):
        if subprocess.run(["pgrep", "-x", "Tuna"], capture_output=True).returncode == 0:
            break
        time.sleep(0.25)
    else:
        raise RuntimeError("Tuna did not restart after installing its settings")
    print("Tuna settings installed and restarted")
elif running:
    subprocess.run([tuna, "config", "reload"], check=True)
    print("Tuna settings installed and reloaded")
else:
    print("Tuna settings installed")
