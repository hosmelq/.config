# Personal setup

Run from this repository on a Mac with Apple's Command Line Tools, Git, mise,
and an App Store account signed in:

```sh
mise bootstrap --force-dotfiles
```

Run it in an interactive terminal: some app installers, App Store packages,
and Portless require a `sudo` password. Quit apps whose preferences are being
replaced before rerunning the bootstrap task.

`mise.toml` installs applications and system packages, links portable config,
and runs the bootstrap task. `mise/config.toml` selects global tools at `latest`;
projects can override versions in their own mise files.

VS Code and PhpStorm sync settings through their accounts. Credentials, sessions,
and generated files stay outside this public repository.

Bootstrap asks for the shared Codex and Claude Executor token and Fish API tokens
on a new machine. It installs Codex settings, Claude's minimal attribution and
Paper-plugin settings, their MCP servers, and the Paper plugin. Credentials
remain local.

After bootstrap, sign in to Codex, Claude, Paper, and Setapp with your own
accounts. Install TablePlus from Setapp to activate its configured MCP server;
the Setapp package alone does not install TablePlus. These sign-ins cannot be
stored in this public repository. Verify with `codex login status`,
`claude auth status`, `claude plugin list --json`, and `codex mcp list`.

Claude's `settings.json` intentionally contains only attribution and Paper
plugin declarations. It does not install a custom permission or sandbox policy.
