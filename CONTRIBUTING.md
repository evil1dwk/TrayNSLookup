# Contributing

Install with `python -m pip install -e ".[build]"`. Run the suite from the
repository root with `python -m unittest discover -s tests -v`.
For GUI tests without a display, set `QT_QPA_PLATFORM=offscreen`.

The GitHub Actions Unit tests workflow runs only when started manually, matching
the other projects and avoiding automatic use of Actions minutes.

Keep release versions in `traynslookup/version.py` using MAJOR.MINOR.PATCH.
Update the changelog for releases, tag `v<version>`, and upload built binaries to
GitHub Releases. Generated output belongs in ignored `build/` and `dist/`
directories. See [Building](docs/BUILDING.md).
