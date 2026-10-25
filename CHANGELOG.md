# Changelog

## [Unreleased]

## [1.4.0] — 2026-10-25

- Name DNS servers while preserving existing address-based settings and selections.
- Highlight records that differ between resolvers with explicit status labels.
- Compare saved structured lookups with fresh results from the same resolvers,
  showing added, removed, and unchanged records and both timestamps.
- Preserve the original history entry and save each new comparison separately.
- Include names and comparison changes in copy/export output and history search.

## [1.3.0] — 2026-10-25

- Add SOA, SRV, CAA, and HTTPS record types.
- Copy selected records or complete results and export text, CSV, or JSON.
- Search history by domain/IP, resolver, query type, and inclusive date range.
- Rerun saved structured queries with their original type and resolvers;
  keep legacy text history readable and exportable.

## [1.2.0] — 2026-10-25

- Automatically convert IPv4 and IPv6 input into PTR reverse lookups.
- Show record names, types, values, and TTLs in tables with responding server
  and query duration metadata.
- Use one persistent server-selection menu for single or multiple resolvers.
- Compare selected DNS servers in parallel, with side-by-side results and
  answer matching that ignores TTL differences and record order.
- Preserve structured query results in history while continuing to read older
  text-only history entries.
- Prevent overlapping runs and wait for active DNS work when quitting.

## [1.1.0] — 2026-10-24

- Add an About button with version, creator credit, repository and issue links.

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
