if test -d /opt/homebrew/bin
    fish_add_path --global --path /opt/homebrew/bin /opt/homebrew/sbin
end

# PHP builds require a newer Bison than the version shipped with macOS.
if test -d /opt/homebrew/opt/bison/bin
    fish_add_path --move --global --path /opt/homebrew/opt/bison/bin
end

if test -d /opt/homebrew/opt/libpq/bin
    fish_add_path --global --path /opt/homebrew/opt/libpq/bin
end

fish_add_path --global --path "$HOME/.composer/vendor/bin"

# Make mise tools available before the remaining conf.d integrations run.
if type -q mise
    mise activate fish --shims | source
end
