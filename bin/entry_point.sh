#!/bin/bash
set -euo pipefail

echo "Entry point script running"

CONFIG_FILE=_config.yml
CONTENT_DIRECTORY=_data/content
CONTENT_POLL_INTERVAL="${CONTENT_POLL_INTERVAL:-2}"

build_content() {
    python3 scripts/build_cv_content.py build
}

# Function to manage Gemfile.lock
manage_gemfile_lock() {
    git config --global --add safe.directory '*'
    if command -v git &> /dev/null && [ -f Gemfile.lock ]; then
        if git ls-files --error-unmatch Gemfile.lock &> /dev/null; then
            echo "Gemfile.lock is tracked by git, keeping it intact"
            git restore Gemfile.lock 2>/dev/null || true
        else
            echo "Gemfile.lock is not tracked by git, removing it"
            rm Gemfile.lock
        fi
    fi
}

start_jekyll() {
    manage_gemfile_lock
    build_content
    bundle exec jekyll serve --watch --port=8080 --host=0.0.0.0 --livereload --verbose --trace --force_polling &
}

start_jekyll

file_snapshot() {
    stat -c '%n %y %s' "$1"
}

content_snapshot() {
    find "$CONTENT_DIRECTORY" -type f -printf '%p %T@ %s\n' | LC_ALL=C sort
}

config_state="$(file_snapshot "$CONFIG_FILE")"
content_state="$(content_snapshot)"

while true; do
    sleep "$CONTENT_POLL_INTERVAL"

    next_config_state="$(file_snapshot "$CONFIG_FILE")"
    next_content_state="$(content_snapshot)"

    if [ "$next_config_state" != "$config_state" ]; then
        echo "Change detected to $CONFIG_FILE, restarting Jekyll"
        jekyll_pid=$(pgrep -f jekyll || true)
        if [ -n "$jekyll_pid" ]; then
            kill -KILL $jekyll_pid
        fi
        start_jekyll
    elif [ "$next_content_state" != "$content_state" ]; then
        echo "Content change detected; regenerating derived content"
        if ! build_content; then
            echo "Content generation failed; retaining the last generated site data." >&2
        fi
    fi

    config_state="$(file_snapshot "$CONFIG_FILE")"
    content_state="$(content_snapshot)"
done
