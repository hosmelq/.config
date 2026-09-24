#!/bin/sh
set -eu

if ! claude plugin marketplace list --json | jq -e '.[] | select(.name == "paper")' >/dev/null; then
    claude plugin marketplace add https://github.com/paper-design/agent-plugins.git
fi

if ! claude plugin list --json | jq -e '.[] | select(.id == "paper-desktop@paper" and .scope == "user")' >/dev/null; then
    claude plugin install paper-desktop@paper --scope user
fi
