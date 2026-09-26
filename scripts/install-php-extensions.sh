#!/bin/sh
set -eu

if [ "$#" -gt 1 ]; then
    echo "Usage: $0 [php-version]" >&2
    exit 2
fi

if [ "$#" -eq 1 ]; then
    php_config="$(mise where "php@$1")/bin/php-config"
else
    php_config="$(mise which php-config)"
fi

if [ ! -x "$php_config" ]; then
    echo "PHP configuration tool not found: $php_config" >&2
    exit 1
fi

php_binary="$(dirname "$php_config")/php"
pie_binary="$(mise which pie)"
set --
if ! "$php_binary" -r 'exit(extension_loaded("anydoc") ? 0 : 1);'; then
    set -- "$@" hosmelq/ext-anydoc
fi
if ! "$php_binary" -r 'exit(extension_loaded("pcov") ? 0 : 1);'; then
    set -- "$@" pecl/pcov
fi
if ! "$php_binary" -r 'exit(extension_loaded("redis") ? 0 : 1);'; then
    set -- "$@" phpredis/phpredis
fi

if [ "$#" -gt 0 ]; then
    "$pie_binary" install --no-interaction --with-php-config="$php_config" "$@"
fi

if ! "$php_binary" -r 'exit(extension_loaded("anydoc") && extension_loaded("pcov") && extension_loaded("redis") ? 0 : 1);'; then
    echo "PHP extensions anydoc, pcov, and redis are not all loaded by $php_binary" >&2
    exit 1
fi
