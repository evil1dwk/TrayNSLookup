# Changelog

## [Unreleased]

- Keep query controls above Results/History tabs in the output area.
- Add Clear Results to clear displayed output while preserving saved history.

- Build directly into `dist/` and create versioned, architecture-specific Windows
  ZIP and Linux tar.gz archives. Include a PNG icon and desktop launcher on Linux.

### Repository structure

- Moved application code and icons into the lowercase `traynslookup` package.
- Added installable package metadata, a desktop command, and a central version.
- Use `python -m traynslookup` to launch the app and preserve the existing user
  configuration path.
- Moved build tools into `scripts/` and platform settings into `packaging/`.
- Removed root launchers; build directly from the package entry point.
- Removed generated executables and the duplicate root icon from the source tree.
- Added contributor, build, and user documentation, regression tests, and a
  manual-only Windows/Linux test workflow.

## [1.0.2]

Existing version recorded in the original Windows and Linux build configurations.
