import os
import unittest
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PyQt6.QtWidgets import QApplication
from traynslookup.ui_mainwindow import MainWindow


class MainWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.cfg = {'dns_servers': ['1.1.1.1'], 'history': [
            {'query': 'example.com', 'result': 'saved result'}]}
        self.window = MainWindow(self.cfg, lambda servers: None)

    def tearDown(self):
        with patch('traynslookup.ui_mainwindow.save_config'):
            self.window.close()

    def test_query_controls_remain_outside_output_tabs(self):
        self.assertIsNot(self.window.centralWidget(), self.window.tabs)
        self.window.tabs.setCurrentWidget(self.window.history_tab)
        self.assertFalse(self.window.tabs.isAncestorOf(self.window.domain_input))
        self.assertEqual([self.window.tabs.tabText(i) for i in range(2)], ['Results', 'History'])

    def test_clear_results_preserves_history_and_query(self):
        self.window.results.setPlainText('test result')
        self.window.domain_input.setText('example.com')
        self.window.clear_results_button.click()
        self.assertEqual(self.window.results.toPlainText(), '')
        self.assertEqual(self.window.domain_input.text(), 'example.com')
        self.assertEqual(len(self.cfg['history']), 1)
        self.assertEqual(self.window.history_list.count(), 1)

    def test_view_history_returns_to_results(self):
        self.window.tabs.setCurrentWidget(self.window.history_tab)
        self.window.history_list.setCurrentRow(0)
        self.window.view_button.click()
        self.assertIs(self.window.tabs.currentWidget(), self.window.lookup_tab)
        self.assertEqual(self.window.results.toPlainText(), 'saved result')

    def test_lookup_from_history_shows_results(self):
        self.window.tabs.setCurrentWidget(self.window.history_tab)
        self.window.domain_input.setText('example.com')
        with patch('traynslookup.ui_mainwindow.DNSLookupThread') as worker:
            self.window.run_button.click()
            worker.return_value.start.assert_called_once()
        self.assertIs(self.window.tabs.currentWidget(), self.window.lookup_tab)
        self.assertIn('Querying example.com', self.window.results.toPlainText())

    def test_about_button_opens_versioned_dialog(self):
        from traynslookup.version import __version__
        self.window.about_button.click()
        dialog = self.window._about_dialog
        self.assertTrue(dialog.isVisible())
        self.assertIn(__version__, dialog.title_label.text())
        self.assertIs(dialog.parentWidget(), self.window)
        self.assertTrue(dialog.links_label.openExternalLinks())
        self.window.about_button.click()
        self.assertIs(self.window._about_dialog, dialog)
        dialog.accept()
        self.assertFalse(dialog.isVisible())
