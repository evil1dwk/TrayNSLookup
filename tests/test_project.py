import importlib
from importlib import metadata, resources
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from traynslookup import __version__
from traynslookup import config
from traynslookup.dns_worker import DNSLookupThread
from scripts.build import ROOT, build_command


class ProjectTests(unittest.TestCase):
    def test_installed_version_and_assets(self):
        self.assertEqual(metadata.version("traynslookup"), __version__)
        for icon in ("TrayNSLookup.ico", "gear.ico"):
            self.assertTrue(resources.files("traynslookup").joinpath("assets", icon).is_file())
            self.assertTrue(config._find_icon(icon).is_file())

    def test_legacy_entry_point(self):
        from traynslookup.main import main
        self.assertIs(importlib.import_module("TrayNSLookup").main, main)

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
                    self.assertEqual(command[-1], str(ROOT / "main.py"))
                    self.assertIn(str(ROOT / "dist" / platform), command)
                    self.assertIn(str(ROOT / "traynslookup" / "assets") + ":traynslookup/assets", command)
        finally:
            os.chdir(previous)

    def test_dns_success_and_failure_without_network(self):
        worker = DNSLookupThread("example.com", "A", "1.1.1.1")
        results = []
        worker.finished.connect(lambda query, result: results.append((query, result)))
        with patch("traynslookup.dns_worker.dns.resolver.Resolver") as factory:
            resolver = factory.return_value
            resolver.resolve.return_value = [type("Answer", (), {"to_text": lambda self: "192.0.2.1"})()]
            worker.run()
            self.assertEqual(resolver.nameservers, ["1.1.1.1"])
            self.assertEqual(results[-1], ("example.com", "192.0.2.1"))
            resolver.resolve.side_effect = RuntimeError("lookup failed")
            worker.run()
            self.assertEqual(results[-1][1], "Error: lookup failed")


if __name__ == "__main__":
    unittest.main()
