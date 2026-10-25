#!/usr/bin/env python3
"""Build from any working directory without modifying tracked source files."""
import argparse
import json
import platform as host_platform
import tarfile
import zipfile
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
                "--distpath", str(ROOT / "dist"),
                "--workpath", str(ROOT / "build" / platform),
                "--specpath", str(ROOT / "build"),
                "--paths", str(ROOT),
                "--add-data", str(ROOT / "traynslookup" / "assets") + ":traynslookup/assets"]
    if platform == "windows":
        command += ["--icon", str(ROOT / "traynslookup" / "assets" / "TrayNSLookup.ico")]
    command.append(str(ROOT / "traynslookup" / "__main__.py"))
    return command


def normalized_architecture():
    arch = host_platform.machine().lower()
    return {"amd64": "x86_64", "x64": "x86_64", "aarch64": "arm64"}.get(arch, arch)


def package_release(platform, project_root=ROOT):
    root = Path(project_root).resolve()
    output = root / "dist"
    binary = output / ("TrayNSLookup.exe" if platform == "windows" else "TrayNSLookup")
    if not binary.is_file():
        raise FileNotFoundError(f"Executable missing: {binary}")
    name = f"TrayNSLookup-{__version__}-{platform}-{normalized_architecture()}"
    if platform == "windows":
        archive = output / f"{name}.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as package:
            package.write(binary, arcname=binary.name)
    elif platform == "linux":
        assets = root / "traynslookup" / "assets"
        files = [binary, assets / "TrayNSLookup.png", assets / "com.evil1dwk.traynslookup.desktop"]
        for file in files:
            if not file.is_file():
                raise FileNotFoundError(f"Linux packaging asset missing: {file}")
        archive = output / f"{name}.tar.gz"
        with tarfile.open(archive, "w:gz") as package:
            for file in files:
                package.add(file, arcname=file.name)
    else:
        raise ValueError(f"Unsupported platform: {platform}")
    return archive


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
    print(f"Release archive: {package_release(platform)}")


if __name__ == "__main__":
    main()
