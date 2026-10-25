import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
from unittest.mock import patch
from PyQt6.QtWidgets import QApplication
from traynslookup.dialogs import ManageDNSServersDialog


class NamedServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_editor_preserves_legacy_and_named_addresses(self):
        dialog = ManageDNSServersDialog(['1.1.1.1', '2001:db8::1'], names={'1.1.1.1':'Cloudflare'})
        self.assertEqual(dialog.get_servers(), ['1.1.1.1','2001:db8::1'])
        self.assertEqual(dialog.get_names(), {'1.1.1.1':'Cloudflare'})
        dialog.accept()
        self.assertEqual(dialog.result(), dialog.DialogCode.Accepted)

    def test_invalid_and_duplicate_addresses_are_rejected(self):
        for servers in [['invalid'], ['1.1.1.1','1.1.1.1']]:
            dialog = ManageDNSServersDialog(servers)
            with patch('traynslookup.dialogs.QMessageBox.warning') as warning:
                dialog.accept()
            warning.assert_called_once()
            self.assertNotEqual(dialog.result(), dialog.DialogCode.Accepted)
