#!/usr/bin/env python3
"""Ask for Fish API tokens that must stay outside the public repository."""

import getpass
import os
from pathlib import Path
import re
import sys
import tempfile


TARGET = Path.home() / ".config/fish/conf.d/variables.fish"
VARIABLES = ("HEROUI_AUTH_TOKEN", "OPENAI_API_KEY")


def fish_quote(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def main() -> None:
    if TARGET.is_symlink():
        raise RuntimeError(f"{TARGET} is a symlink; refusing to replace it")
    before = TARGET.stat() if TARGET.exists() else None
    current = TARGET.read_text() if before else ""
    installed = set(re.findall(r"(?m)^\s*set\s+-gx\s+([A-Z][A-Z0-9_]*)\s+\S", current))
    missing = [name for name in VARIABLES if name not in installed]
    if not missing:
        if before and before.st_mode & 0o077:
            TARGET.chmod(0o600)
        return
    if not sys.stdin.isatty():
        raise RuntimeError("Run mise bootstrap in an interactive terminal to enter Fish API tokens")

    additions = []
    for name in missing:
        value = getpass.getpass(f"{name}: ")
        if not value or "\n" in value or "\r" in value:
            raise RuntimeError(f"{name} must be a nonempty single-line value")
        additions.append(f"set -gx {name} {fish_quote(value)}\n")

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{TARGET.name}.", dir=TARGET.parent)
    try:
        with os.fdopen(handle, "w") as output:
            output.write(current.rstrip("\n") + ("\n\n" if current else "") + "".join(additions))
        os.chmod(temporary, 0o600)
        if before:
            now = TARGET.stat()
            if (now.st_mtime_ns, now.st_size) != (before.st_mtime_ns, before.st_size):
                raise RuntimeError(f"{TARGET} changed during installation; retry")
        elif TARGET.exists():
            raise RuntimeError(f"{TARGET} appeared during installation; retry")
        os.replace(temporary, TARGET)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print("Fish API tokens installed locally")


if __name__ == "__main__":
    main()
