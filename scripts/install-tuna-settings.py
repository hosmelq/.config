#!/usr/bin/env python3
"""Install Tuna's portable configuration and reload it when Tuna is running."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


source = Path(sys.argv[1])
destination = Path.home() / "Library/Application Support/Tuna/config.toml"
contents = source.read_text().replace("__HOME__", str(Path.home()))

if destination.exists() and destination.read_text() == contents:
    print("Tuna settings already match")
    sys.exit(0)

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

if subprocess.run(["pgrep", "-x", "Tuna"], capture_output=True).returncode == 0:
    tuna = shutil.which("tuna")
    if tuna is None:
        print("Tuna settings installed; restart Tuna to apply them")
    else:
        subprocess.run([tuna, "config", "reload"], check=True)
        print("Tuna settings installed and reloaded")
else:
    print("Tuna settings installed")
