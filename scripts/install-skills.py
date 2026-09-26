#!/usr/bin/env python3
"""Restore missing global skills, then update the tracked upstream skills."""

from collections import defaultdict
import json
import os
from pathlib import Path
import subprocess
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
MANIFEST = ROOT / "dotfiles/agents/.skill-lock.json"


def source_identity(entry):
    return {key: entry.get(key) for key in (
        "source", "sourceType", "sourceUrl", "ref", "skillPath", "skillFolderHash"
    )}


def install():
    lock_path = HOME / ".agents/.skill-lock.json"
    if not lock_path.is_symlink() or lock_path.resolve() != MANIFEST.resolve():
        raise RuntimeError(
            "Link the repository skill lock first: "
            "mise dot apply --yes ~/.agents/.skill-lock.json"
        )
    # The CLI can use a different lock when XDG_STATE_HOME is set. This setup
    # deliberately uses the repository-backed ~/.agents lock on both machines.
    environment = os.environ.copy()
    environment.pop("XDG_STATE_HOME", None)
    manifest = json.loads(MANIFEST.read_text())
    state_path = HOME / ".agents/.skill-install-state.json"
    state = json.loads(state_path.read_text()) if state_path.is_file() else {}
    groups = defaultdict(list)
    for name, entry in manifest["skills"].items():
        if (state.get(name) != source_identity(entry)
                or not (HOME / ".agents/skills" / name / "SKILL.md").is_file()):
            source = entry["sourceUrl"]
            if entry.get("ref"):
                if entry["sourceType"] != "github":
                    raise RuntimeError(f"Unsupported pinned skill source: {name}")
                source = f'https://github.com/{entry["source"]}/tree/{quote(entry["ref"], safe="")}'
            groups[source].append(name)

    for source, names in sorted(groups.items()):
        subprocess.run(
            ["nubx", "-y", "skills", "add", source, "--global", "--yes",
             "--full-depth", "--agent", "codex", "claude-code", "--skill", *sorted(names)],
            check=True, env=environment,
        )

    subprocess.run(
        ["nubx", "-y", "skills", "update", "--global", "--yes"],
        check=True, env=environment,
    )
    missing = sorted(
        name for name in manifest["skills"]
        if not (HOME / ".agents/skills" / name / "SKILL.md").is_file()
    )
    if missing:
        raise RuntimeError("Skills were not installed: " + ", ".join(missing))
    if not lock_path.is_symlink() or lock_path.resolve() != MANIFEST.resolve():
        raise RuntimeError("The skills CLI replaced the repository lock symlink")
    # Each Mac needs its own receipt: a newer repository lock does not mean
    # that machine has already installed the corresponding skill files.
    current = json.loads(MANIFEST.read_text())
    state_path.write_text(json.dumps({
        name: source_identity(entry) for name, entry in current["skills"].items()
    }, indent=2) + "\n")
    print(f'Installed global skills verified: {len(manifest["skills"])}')


if __name__ == "__main__":
    install()
