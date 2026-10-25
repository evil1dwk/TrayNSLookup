# TrayNSLookup

A lightweight DNS lookup utility for Windows and Linux, built with Python and PyQt6.
It runs in the system tray and keeps lookup history between sessions.

## Features

- Look up A, AAAA, CNAME, MX, TXT, NS, PTR, SOA, SRV, CAA, and HTTPS records.
- Enter IPv4 or IPv6 addresses for automatic reverse lookup.
- Inspect structured records with TTL, responding resolver, and query duration.
- Name DNS servers and compare their answers with highlighted differences.
- Compare saved results with fresh lookups to see records added or removed.
- Use the system resolver or choose a custom DNS server.
- Manage DNS servers from the lookup window or tray menu.
- Search saved results by domain, server, type, or date and rerun queries.
- Copy selected records or all results; export text, CSV, or JSON.
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

## Build

```bash
python -m pip install -e ".[build]"
python scripts/build.py
```

## Project layout

| Path | Purpose |
| --- | --- |
| `traynslookup/` | Application, dialogs, DNS worker, configuration, and bundled assets |
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
