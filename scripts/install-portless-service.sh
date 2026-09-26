#!/bin/sh
set -eu

status=$(portless service status 2>/dev/null || true)
case "$status" in
    *"Manager state: running"*"Installed: yes"*"TLDs: .localhost"*"Wildcard: yes"*)
        exit 0
        ;;
esac

portless service install --tld localhost --wildcard
