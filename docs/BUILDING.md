# Building TrayNSLookup

Use Python 3.11+ on Windows or Linux. Build on the OS you intend to run on;
PyInstaller does not cross-compile.

```bash
python -m pip install -e ".[build]"
python -m unittest discover -s tests -v
python scripts/build.py
```

The build script resolves source and asset paths relative to the repository,
so it can also be run
by absolute path from another directory. Full build logs are shown by default;
`--verbose` remains accepted.

The script uses the current Python interpreter to run PyInstaller. It bundles
icons from `traynslookup/assets/` and writes temporary files under `build/`.
Tracked platform configuration lives in `packaging/windows/build.json` and
`packaging/linux/build.json`; customize flags there or pass `--config PATH`.

| Platform | Output |
| --- | --- |
| Windows | `dist/TrayNSLookup.exe` and `dist/TrayNSLookup-<version>-windows-<arch>.zip` |
| Linux | `dist/TrayNSLookup` and `dist/TrayNSLookup-<version>-linux-<arch>.tar.gz` |

Windows builds are standalone executables. There is currently no Inno Setup
script in this repository, so the build does not generate an installer. macOS
packaging is not configured.

## Releases

Set `traynslookup/version.py`, update `CHANGELOG.md`, test, and tag the release
as `v<version>`. Build the tagged source on each supported OS and upload the
resulting binaries or archives to GitHub Releases. Building does not change the
release version or delete source files.

## Linux desktop launcher

The Linux tar.gz contains `TrayNSLookup`, `TrayNSLookup.png`, and
`com.evil1dwk.traynslookup.desktop` at its top level. After extracting, install
for the current user from that directory:

```bash
mkdir -p ~/.local/bin ~/.local/share/applications ~/.local/share/icons/hicolor/128x128/apps
install -m 755 TrayNSLookup ~/.local/bin/TrayNSLookup
install -m 644 TrayNSLookup.png ~/.local/share/icons/hicolor/128x128/apps/TrayNSLookup.png
install -m 644 com.evil1dwk.traynslookup.desktop ~/.local/share/applications/
```

Ensure `~/.local/bin` is on your desktop session's PATH (log out and back in if
needed). The desktop launcher uses `Exec=TrayNSLookup` and `Icon=TrayNSLookup`,
which resolve through PATH and the installed icon theme. To run from an arbitrary
extracted folder instead, use `./TrayNSLookup`; the desktop file expects installation.
