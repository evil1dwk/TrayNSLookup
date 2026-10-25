import importlib
from importlib import metadata, resources
import os
from pathlib import Path
import tempfile
import tarfile
import zipfile
import shutil
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from traynslookup import __version__
from traynslookup import config
from traynslookup.dns_worker import DNSLookupThread
from scripts.build import ROOT, build_command, package_release


class ProjectTests(unittest.TestCase):
    def test_installed_version_and_assets(self):
        self.assertEqual(metadata.version("traynslookup"), __version__)
        for icon in ("TrayNSLookup.ico", "gear.ico"):
            self.assertTrue(resources.files("traynslookup").joinpath("assets", icon).is_file())
            self.assertTrue(config._find_icon(icon).is_file())

    def test_module_entry_point(self):
        from traynslookup.main import main
        self.assertIs(importlib.import_module("traynslookup.__main__").main, main)

    def test_config_round_trip_and_defaults(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(config, "CONFIG_PATH", Path(folder) / "config.json"):
                cfg = config.load_config()
                self.assertEqual(cfg["dns_servers"], config.DEFAULT_DNS_SERVERS)
                cfg["history"].append({"query": "example.com", "result": "test"})
                cfg["window"] = {"size": [760, 540], "pos": [10, 20]}
                config.save_config(cfg)
                self.assertEqual(config.load_config(), cfg)
                config.CONFIG_PATH.write_text("invalid", encoding="utf-8")
                self.assertEqual(config.load_config()["history"], [])

    def test_build_paths_from_other_directory(self):
        previous = Path.cwd()
        try:
            with tempfile.TemporaryDirectory() as folder:
                os.chdir(folder)
                for platform in ("windows", "linux"):
                    command = build_command(platform)
                    self.assertEqual(command[-1], str(ROOT / "traynslookup" / "__main__.py"))
                    self.assertIn(str(ROOT / "dist"), command)
                    self.assertIn(str(ROOT / "traynslookup" / "assets") + ":traynslookup/assets", command)
        finally:
            os.chdir(previous)

    def test_release_archives(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "dist").mkdir()
            assets = root / "traynslookup" / "assets"
            shutil.copytree(ROOT / "traynslookup" / "assets", assets)
            binary = root / "dist" / "TrayNSLookup"
            binary.write_bytes(b"linux executable")
            binary.chmod(0o755)
            (root / "dist" / "TrayNSLookup.exe").write_bytes(b"windows executable")
            with patch("scripts.build.host_platform.machine", return_value="AMD64"):
                linux = package_release("linux", root)
                self.assertEqual(linux.name, f"TrayNSLookup-{__version__}-linux-x86_64.tar.gz")
                with tarfile.open(linux) as archive:
                    self.assertEqual(set(archive.getnames()), {
                        "TrayNSLookup", "TrayNSLookup.png", "com.evil1dwk.traynslookup.desktop"})
                    self.assertEqual(archive.extractfile("TrayNSLookup").read(), b"linux executable")
                    if os.name != "nt":
                        self.assertTrue(archive.getmember("TrayNSLookup").mode & 0o111)
                    desktop = archive.extractfile("com.evil1dwk.traynslookup.desktop").read().decode()
                    self.assertIn("Exec=TrayNSLookup\n", desktop)
                    self.assertIn("Icon=TrayNSLookup\n", desktop)
                windows = package_release("windows", root)
                self.assertEqual(windows.name, f"TrayNSLookup-{__version__}-windows-x86_64.zip")
                with zipfile.ZipFile(windows) as archive:
                    self.assertEqual(archive.namelist(), ["TrayNSLookup.exe"])
                    self.assertEqual(archive.read("TrayNSLookup.exe"), b"windows executable")
                binary.unlink()
                with self.assertRaises(FileNotFoundError):
                    package_release("linux", root)


if __name__ == "__main__":
    unittest.main()
