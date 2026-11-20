#!/bin/sh
set -eu

case "${1-}:$#" in
    codex:1) install_command=add ;;
    claude:1) install_command=install ;;
    *) echo "Usage: $0 codex|claude" >&2; exit 2 ;;
esac

client=$1
"$client" plugin marketplace add https://github.com/btwld/agent-plugins.git
"$client" plugin "$install_command" bitwild-team-kit@conceptadev
"$client" plugin marketplace add https://github.com/flutter/agent-plugins.git
"$client" plugin "$install_command" dart-flutter@dart-flutter
