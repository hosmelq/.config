# Personal setup

Run from this repository on a Mac with Apple's Command Line Tools, Git, mise,
and an App Store account signed in:

```sh
# Mac mini: shared setup only.
mise bootstrap --force-dotfiles

# MacBook: shared setup plus laptop applications.
mise -E macbook bootstrap --force-dotfiles
```

Run it in an interactive terminal: some app installers, App Store packages,
and Portless require a `sudo` password. Quit apps whose preferences are being
replaced before rerunning the bootstrap task.

`mise.toml` installs applications and system packages, links portable config,
and runs the bootstrap task. `mise/config.toml` selects global tools at `latest`;
projects can override versions in their own mise files.

`mise.macbook.toml` adds the laptop-only applications. The Mac mini uses only
the shared packages in `mise.toml`. Selecting a profile does not uninstall
applications already present on a machine.

VS Code and PhpStorm sync settings through their accounts. Credentials, sessions,
and generated files stay outside this public repository.

Bootstrap asks for the shared Codex and Claude Executor token and Fish API tokens
on a new machine. It installs Codex settings, Claude's minimal attribution and
Paper-plugin settings, their MCP servers, and the Paper plugin. Credentials
remain local. Codex project trust, interface notices, and the desktop browser
runtime configuration are preserved on each machine when settings are applied.
Run `mise run config:codex` to apply only Codex settings.

Bootstrap also installs missing global skills from the linked
`~/.agents/.skill-lock.json`, then runs `nubx -y skills update --global --yes`.
Run `mise run skills:sync` to repeat only this step. A local install receipt in
`~/.agents/.skill-install-state.json` ensures each Mac installs changes pulled
from the repository, even when the skill directories already exist.
The CLI updates the linked
lock in this repository; commit its changes when keeping the two Macs in sync.
Skills supplied directly by an application or installed outside this lock keep
that application's installation and update mechanism.

After bootstrap, sign in to Codex, Claude, Paper, and Setapp with your own
accounts. Install TablePlus from Setapp to activate its configured MCP server;
the Setapp package alone does not install TablePlus. These sign-ins cannot be
stored in this public repository. Verify with `codex login status`,
`claude auth status`, `claude plugin list --json`, and `codex mcp list`.

Claude's `settings.json` intentionally contains only attribution and Paper
plugin declarations. It does not install a custom permission or sandbox policy.
