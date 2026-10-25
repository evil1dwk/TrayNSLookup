# TrayNSLookup

A lightweight DNS lookup utility for Windows and Linux, built with Python and PyQt6.
It runs in the system tray and keeps lookup history between sessions.

## Features

- Look up A, AAAA, CNAME, MX, TXT, NS, and PTR records.
- Use the system resolver or choose a custom DNS server.
- Manage DNS servers from the lookup window or tray menu.
- Review saved results in the History tab.
- Restore window size and position.

## Install and run

Python **3.11 or newer** is required. From the repository root:

```bash
python -m venv .venv
# Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e .
python -m traynslookup
```

You can also use `traynslookup`, `python main.py`, or the original
`python -m TrayNSLookup` command.

## Project layout

| Path | Purpose |
| --- | --- |
| `traynslookup/` | Application, dialogs, DNS worker, configuration, and bundled assets |
| `TrayNSLookup.py` | Compatibility for the original module command |
| `scripts/` | Build tools |
| `packaging/` | Tracked platform build configuration |
| `tests/` | Unit and packaging regression tests |
| `docs/` | Build instructions and user guide |
| `build/`, `dist/` | Generated output, ignored by Git |

See [Building](docs/BUILDING.md), [User guide](docs/USER_GUIDE.md),
[Contributing](CONTRIBUTING.md), and [Changelog](CHANGELOG.md).

## Downloads

Publish executable downloads as assets on [GitHub Releases](https://github.com/evil1dwk/TrayNSLookup/releases).
Compiled binaries are no longer stored in the source tree. Older binaries remain
available in Git history; this restructuring does not rewrite repository history.
