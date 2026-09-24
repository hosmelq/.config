#!/bin/sh
set -eu

python ./scripts/install-agent-config.py
./scripts/install-claude-plugins.sh
python3 ./scripts/install-fish-variables.py
./scripts/install-npm-tools.sh
./scripts/install-portless-service.sh
composer global install --no-interaction
if ! gh auth status >/dev/null 2>&1; then
    gh auth login
fi
gh extension install basecamp/gh-signoff --force
gh extension install github/gh-stack --force
mise bootstrap packages apply --manager mas --yes
swift ./scripts/install-app-settings.swift ./dotfiles/macos/app-settings.json
python3 ./scripts/install-tuna-settings.py ./dotfiles/tuna/config.toml.tmpl
