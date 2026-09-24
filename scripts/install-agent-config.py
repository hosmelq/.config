#!/usr/bin/env python3
"""Install Codex and Claude settings, keeping local hooks and secrets local."""

import getpass
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import tomllib


ROOT = Path(__file__).resolve().parent.parent
HOME = Path.home()
TOKEN_MARKER = 'Authorization = "Bearer __CODEX_EXECUTOR_TOKEN__"'


def write_private(path: Path, content: str, before: os.stat_result | None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(handle, "w") as output:
            output.write(content)
        os.chmod(temporary, 0o600)
        if before is not None:
            now = path.stat()
            if (now.st_mtime_ns, now.st_size) != (before.st_mtime_ns, before.st_size):
                raise RuntimeError(f"{path} changed during installation; retry")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def local_codex_sections(content: str) -> str:
    local_headers = (
        "[hooks",
        "[marketplaces.",
        "[mcp_servers.computer-use",
        "[mcp_servers.node_repl",
        "[notice",
        "[projects.",
        '[permissions.development-safe.filesystem."~/Code/',
        "[shell_environment_policy.set]",
        "[tui.model_availability_nux]",
    )
    lines = content.splitlines(keepends=True)
    sections = []
    start = None
    for index, line in enumerate(lines):
        if line.startswith("["):
            if start is not None:
                sections.append("".join(lines[start:index]))
                start = None
            header = line.split("]", 1)[0] + "]"
            if header.startswith(local_headers):
                start = index
    if start is not None:
        sections.append("".join(lines[start:]))
    return "\n".join(section.rstrip("\n") for section in sections)


def install_codex() -> str:
    target = HOME / ".codex/config.toml"
    if target.is_symlink():
        raise RuntimeError(f"{target} is a symlink; refusing to replace it")
    before = target.stat() if target.exists() else None
    current_text = target.read_text() if before else ""
    current = tomllib.loads(current_text) if current_text else {}
    auth = current.get("mcp_servers", {}).get("executor", {}).get("http_headers", {}).get("Authorization", "")
    token = auth[7:] if isinstance(auth, str) and auth.startswith("Bearer ") else ""
    if not token:
        if not sys.stdin.isatty():
            raise RuntimeError("Run mise bootstrap in an interactive terminal to enter the Codex Executor token")
        token = getpass.getpass("Codex Executor token: ").strip()
        if not token:
            raise RuntimeError("Codex Executor token is required")

    template = (ROOT / "dotfiles/agents/codex-config.toml.tmpl").read_text()
    if template.count(TOKEN_MARKER) != 1:
        raise RuntimeError("Codex template must contain exactly one token marker")
    desired = template.replace(TOKEN_MARKER, "Authorization = " + json.dumps("Bearer " + token))

    root = current_text.split("\n[", 1)[0]
    notify = re.search(r"(?m)^notify\s*=.*$", root)
    if notify:
        first_section = desired.find("\n[")
        desired = desired[:first_section] + "\n" + notify.group(0) + desired[first_section:]
    local_sections = local_codex_sections(current_text)
    if local_sections:
        desired = desired.rstrip("\n") + "\n\n" + local_sections + "\n"

    if current and tomllib.loads(desired) == current:
        if target.stat().st_mode & 0o077:
            os.chmod(target, 0o600)
        return token
    tomllib.loads(desired)
    write_private(target, desired, before)
    print("Codex configuration installed")
    return token


def install_claude() -> None:
    target = HOME / ".claude/settings.json"
    if target.is_symlink():
        raise RuntimeError(f"{target} is a symlink; refusing to replace it")
    before = target.stat() if target.exists() else None
    current = json.loads(target.read_text()) if before else {}
    desired = json.loads((ROOT / "dotfiles/agents/claude-settings.json").read_text())
    for key in ("hooks", "statusLine"):
        if key in current:
            desired[key] = current[key]
    if current.get("enabledPlugins"):
        desired["enabledPlugins"] = current["enabledPlugins"]
    local_auto_mode = current.get("autoMode", {})
    if isinstance(local_auto_mode, dict) and "environment" in local_auto_mode:
        desired.setdefault("autoMode", {})["environment"] = local_auto_mode["environment"]
    if desired == current:
        if target.stat().st_mode & 0o077:
            os.chmod(target, 0o600)
        return
    write_private(target, json.dumps(desired, ensure_ascii=False, indent=2) + "\n", before)
    print("Claude configuration installed")


def install_claude_mcp(token: str) -> None:
    target = HOME / ".claude.json"
    if target.is_symlink():
        raise RuntimeError(f"{target} is a symlink; refusing to replace it")
    before = target.stat() if target.exists() else None
    current = json.loads(target.read_text()) if before else {}
    servers = json.loads((ROOT / "dotfiles/agents/claude-mcp-servers.json").read_text())
    marker = "Bearer __CODEX_EXECUTOR_TOKEN__"
    if servers["executor"]["headers"]["Authorization"] != marker:
        raise RuntimeError("Claude MCP template must contain the Executor token marker")
    servers["executor"]["headers"]["Authorization"] = "Bearer " + token
    desired = current.copy()
    desired.setdefault("mcpServers", {}).update(servers)
    if desired == current:
        if target.stat().st_mode & 0o077:
            os.chmod(target, 0o600)
        return
    write_private(target, json.dumps(desired, ensure_ascii=False, indent=2) + "\n", before)
    print("Claude MCP servers installed")


if __name__ == "__main__":
    executor_token = install_codex()
    install_claude()
    install_claude_mcp(executor_token)
