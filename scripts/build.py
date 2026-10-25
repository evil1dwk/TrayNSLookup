#!/usr/bin/env python3
"""Build from any working directory without modifying tracked source files."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from traynslookup.version import __version__


def build_command(platform, config=None):
    config_path = Path(config).resolve() if config else ROOT / "packaging" / platform / "build.json"
    settings = json.loads(config_path.read_text(encoding="utf-8"))
    command = [sys.executable, "-m", "PyInstaller", *settings["pyinstaller"]]
    command += ["--name", settings["AppName"],
                "--distpath", str(ROOT / "dist" / platform),
                "--workpath", str(ROOT / "build" / platform),
                "--specpath", str(ROOT / "build"),
                "--paths", str(ROOT),
                "--add-data", str(ROOT / "traynslookup" / "assets") + ":traynslookup/assets"]
    if platform == "windows":
        command += ["--icon", str(ROOT / "traynslookup" / "assets" / "TrayNSLookup.ico")]
    command.append(str(ROOT / "traynslookup" / "__main__.py"))
    return command


def main():
    parser = argparse.ArgumentParser(description="Build TrayNSLookup on the current OS.")
    parser.add_argument("-c", "--config", help="Optional build JSON path")
    parser.add_argument("--verbose", action="store_true", help="Show full build output (default)")
    args = parser.parse_args()
    platform = {"win32": "windows", "linux": "linux"}.get(sys.platform)
    if platform is None:
        parser.error("Executable packaging is currently supported on Windows and Linux.")
    print(f"Building TrayNSLookup {__version__} for {platform}")
    (ROOT / "build").mkdir(exist_ok=True)
    subprocess.run(build_command(platform, args.config), cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
