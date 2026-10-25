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
| Windows | `dist/windows/TrayNSLookup.exe` |
| Linux | `dist/linux/TrayNSLookup` |

Windows builds are standalone executables. There is currently no Inno Setup
script in this repository, so the build does not generate an installer. macOS
packaging is not configured.

## Releases

Set `traynslookup/version.py`, update `CHANGELOG.md`, test, and tag the release
as `v<version>`. Build the tagged source on each supported OS and upload the
resulting binaries or archives to GitHub Releases. Building does not change the
release version or delete source files.
