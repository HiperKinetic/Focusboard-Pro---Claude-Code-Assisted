# Focusboard PRO — macOS Desktop App

A native macOS window running the full Focusboard PRO project manager,
powered by Python + pywebview. Data is saved automatically to your Mac.

---

## Requirements

- macOS 10.14 or later
- Python 3.8+ (ships with macOS, or install via https://python.org)

---

## Install (one time)

Open **Terminal** and run:

```bash
pip3 install pywebview
```

If you get a permissions error, use:

```bash
pip3 install pywebview --user
```

---

## Run

Double-click **run.command** in Finder  
— OR —  
In Terminal:

```bash
cd /path/to/FocusboardPRO
python3 focusboard.py
```

---

## Data Storage

All your data is saved automatically to:

```
~/Library/Application Support/FocusboardPRO/data.json
```

This means:
- Data **persists** across sessions
- You can **back it up** by copying that file
- You can **transfer** to another Mac by copying it there

---

## Features

| View | Description |
|------|-------------|
| Task List | Full task management with subtasks, owners, dates |
| Kanban | Drag-and-drop board across 4 status lanes |
| By Owner | Workload grouped per team member |
| Milestones | Track milestones with task dependencies |
| Status Updates | Green / Yellow / Red / Blocked reports with PTG |
| Timeline | Gantt chart — planned vs actual, milestone markers |
| Critical Path | CPM analysis, slack, float, variance table |

**Undo** — every change is undoable (40-step history)  
**Auto-save** — saves to disk 400ms after each change  
**Multiple projects** — create as many as you need from the sidebar

---

## Troubleshooting

**"command not found: pip3"**  
Install Python from https://python.org/downloads

**App opens but shows blank screen**  
You need an internet connection on first launch to load fonts from Google.
After first load it works offline.

**pywebview install fails on Apple Silicon**  
Try: `pip3 install pywebview --no-binary :all:`
