#!/bin/bash
# ─────────────────────────────────────────────
#  Focusboard PRO — macOS Installer
#  Double-click this file to install everything
# ─────────────────────────────────────────────

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── Helper: show a dialog ─────────────────────
alert() {
  osascript -e "display alert \"Focusboard PRO\" message \"$1\""
}

notify() {
  osascript -e "display notification \"$1\" with title \"Focusboard PRO\""
}

# ── 1. Check Python 3 ─────────────────────────
echo "Checking Python 3..."
if ! command -v python3 &>/dev/null; then
  alert "Python 3 is not installed.\n\nOpening python.org for you — download and install Python 3, then run this installer again."
  open "https://www.python.org/downloads/"
  exit 1
fi
PY_VER=$(python3 --version 2>&1)
echo "Found: $PY_VER"

# ── 2. Install / upgrade pywebview ───────────
echo "Installing pywebview..."
python3 -m pip install --upgrade pywebview --quiet 2>&1 || \
python3 -m pip install --upgrade pywebview --user --quiet 2>&1 || {
  alert "Could not install pywebview automatically.\n\nPlease run this in Terminal:\n\npip3 install pywebview\n\nThen double-click run.command to launch."
  exit 1
}
echo "pywebview installed."

# ── 3. Install app to ~/Applications ─────────
DEST="$HOME/Applications/FocusboardPRO"
echo "Installing app to $DEST..."
mkdir -p "$DEST"
cp "$SCRIPT_DIR/focusboard.py" "$DEST/focusboard.py"

# Write the launcher into place
cat > "$DEST/Focusboard PRO.command" << 'LAUNCHER'
#!/bin/bash
cd "$(dirname "$0")"
python3 focusboard.py
LAUNCHER
chmod +x "$DEST/Focusboard PRO.command"

# ── 4. Create a Desktop shortcut ─────────────
SHORTCUT="$HOME/Desktop/Focusboard PRO.command"
cp "$DEST/Focusboard PRO.command" "$SHORTCUT"
# Point the shortcut's cd to the installed location
cat > "$SHORTCUT" << SHORTCUTEOF
#!/bin/bash
cd "$DEST"
python3 focusboard.py
SHORTCUTEOF
chmod +x "$SHORTCUT"

# ── 5. Add shell alias (zsh + bash) ──────────
ALIAS_LINE='alias focusboard="python3 '"$DEST"'/focusboard.py"'

for RC in "$HOME/.zshrc" "$HOME/.bashrc"; do
  if [ -f "$RC" ] || [ "$RC" = "$HOME/.zshrc" ]; then
    if ! grep -q "alias focusboard=" "$RC" 2>/dev/null; then
      echo "" >> "$RC"
      echo "# Focusboard PRO" >> "$RC"
      echo "$ALIAS_LINE" >> "$RC"
      echo "Added alias to $RC"
    fi
  fi
done

# ── 6. Add to Login Items so it's easy to find ─
# (We don't auto-launch on startup — just notify where it lives)

# ── 7. Launch it now ─────────────────────────
echo ""
echo "✓ Installation complete!"
echo "  App installed to: $DEST"
echo "  Desktop shortcut: $SHORTCUT"
echo "  Shell alias:      focusboard"
echo ""
echo "Launching Focusboard PRO..."
echo ""

osascript << APPLESCRIPT
display notification "Focusboard PRO installed successfully!
• Desktop shortcut created
• Type 'focusboard' in Terminal to launch
• Data saves to ~/Library/Application Support/FocusboardPRO/" with title "Focusboard PRO ✓"
APPLESCRIPT

# Launch the app
python3 "$DEST/focusboard.py"
