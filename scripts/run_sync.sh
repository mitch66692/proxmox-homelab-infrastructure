#!/bin/bash
# scripts/run_sync.sh
# Wrapper script executed by Cron to set up the environment and trigger the Python sync tool.

# Define the target playlist URL (Placeholder for public repository)
PLAYLIST_URL="https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"

# Path to the Python script
SCRIPT_PATH="/data/scripts/spotify_sync.py"

# Ensure the script is executed using the correct Python interpreter and passes the URL argument
if [ -f "$SCRIPT_PATH" ]; then
    /usr/bin/python3 "$SCRIPT_PATH" "$PLAYLIST_URL"
else
    echo "ERROR: Target Python script not found at $SCRIPT_PATH" >&2
    exit 1
fi
