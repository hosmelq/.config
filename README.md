# Personal setup

Run from this repository on a Mac with Apple's Command Line Tools, Git, mise,
and an App Store account signed in:

```sh
mise bootstrap --force-dotfiles
```

`mise.toml` installs applications and system packages, links portable config,
and runs the bootstrap task. `mise/config.toml` selects global tools at `latest`;
projects can override versions in their own mise files.

VS Code and PhpStorm sync settings through their accounts. Credentials, sessions,
and generated files stay outside this public repository.

Bootstrap asks for the shared Codex and Claude Executor token and Fish API tokens
on a new machine. Agent hooks and credentials remain local.
