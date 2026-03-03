#!/bin/bash
# Focusboard PRO launcher
# Double-click this file in Finder to launch the app

cd "$(dirname "$0")"

# Check Python
if ! command -v python3 &>/dev/null; then
  osascript -e 'display alert "Python 3 not found" message "Please install Python 3 from https://python.org and try again." as critical'
  exit 1
fi

# Check pywebview
if ! python3 -c "import webview" &>/dev/null; then
  osascript -e 'display alert "pywebview not installed" message "Run this in Terminal:\n\npip3 install pywebview\n\nThen launch Focusboard again." as critical'
  exit 1
fi

python3 focusboard.py
