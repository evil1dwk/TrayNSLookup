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
        self.save_patch = patch('traynslookup.ui_mainwindow.save_config')
        self.save_patch.start()
        self.window = MainWindow(self.cfg, lambda servers: None)

    def tearDown(self):
        self.window._lookup_finished()
        with patch('traynslookup.ui_mainwindow.save_config'):
            self.window.close()
        self.save_patch.stop()

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

    def test_structured_result_history_and_clear(self):
        lookup = {'query': 'example.com', 'comparison': 'Answers match', 'results': [
            {'requested_server': server, 'server': server, 'elapsed_ms': 12,
             'record_type': 'A', 'error': '', 'records': [
                 {'name': 'example.com.', 'type': 'A', 'value': '192.0.2.1', 'ttl': 60}]}
            for server in ['1.1.1.1', '8.8.8.8']]}
        with patch('traynslookup.ui_mainwindow.save_config'):
            self.window._display_result(lookup)
        self.assertEqual(len(self.window.result_tables), 2)
        self.assertEqual(self.window.result_tables[0].item(0, 3).text(), '60')
        self.assertIs(self.window.result_stack.currentWidget(), self.window.structured_results)
        self.window.clear_results_button.click()
        self.assertEqual(len(self.cfg['history']), 2)
        self.assertEqual(self.window.structured_layout.count(), 0)
        self.window.history_list.setCurrentRow(0)
        self.window.view_button.click()
        self.assertEqual(len(self.window.result_tables), 2)

    def test_compare_selection_and_reverse_query(self):
        self.cfg['dns_servers'].append('8.8.8.8')
        self.window._reload_compare_servers()
        for action in self.window.server_actions:
            action.setChecked(action.data() is not None)
        self.window.domain_input.setText('2001:db8::1')
        with patch('traynslookup.ui_mainwindow.DNSLookupThread') as worker:
            self.window.run_button.click()
            worker.assert_called_once_with('2001:db8::1', 'PTR', ['1.1.1.1', '8.8.8.8'])
            self.window._run_lookup()
            self.assertEqual(worker.call_count, 1)
        self.assertFalse(self.window.run_button.isEnabled())
        self.window._lookup_finished()
        self.assertTrue(self.window.run_button.isEnabled())

    def test_lookup_requires_at_least_one_server(self):
        self.window.domain_input.setText('example.com')
        for action in self.window.server_actions:
            action.setChecked(False)
        with patch('traynslookup.ui_mainwindow.QMessageBox.warning') as warning:
            self.window._run_lookup()
            warning.assert_called_once()
        self.assertFalse(self.window._lookup_running)

    def test_real_worker_delivers_results_to_window(self):
        from PyQt6.QtCore import QEventLoop, QTimer
        self.window.domain_input.setText('example.com')
        result = dict(query='example.com', name='example.com', record_type='A',
                      requested_server='1.1.1.1', server='1.1.1.1', elapsed_ms=1,
                      records=[dict(name='example.com.', type='A', value='192.0.2.1', ttl=60)], error='')
        with patch('traynslookup.dns_worker.lookup_server', return_value=result), \
             patch('traynslookup.ui_mainwindow.save_config'):
            self.window._run_lookup()
            loop = QEventLoop()
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(loop.quit)
            timer.start(3000)
            self.window.worker.finished.connect(loop.quit)
            loop.exec()
            self.window.worker.wait()
            self.app.processEvents()
        self.assertFalse(self.window._lookup_running)
        self.assertEqual(self.window.result_tables[0].item(0, 2).text(), '192.0.2.1')
        self.assertIn('lookup', self.cfg['history'][-1])

    def test_single_server_and_selection_persistence(self):
        for action in self.window.server_actions:
            action.setChecked(action.data() == '1.1.1.1')
        self.assertEqual(self.cfg['selected_dns_servers'], ['1.1.1.1'])
        self.window.domain_input.setText('example.com')
        with patch('traynslookup.ui_mainwindow.DNSLookupThread') as worker:
            self.window._run_lookup()
            worker.assert_called_once_with('example.com', 'A', ['1.1.1.1'])
        restored = MainWindow(self.cfg, lambda servers: None)
        self.assertEqual([a.data() for a in restored.server_actions if a.isChecked()], ['1.1.1.1'])
        restored.close()

    def test_empty_selection_survives_restart(self):
        for action in self.window.server_actions:
            action.setChecked(False)
        restored = MainWindow(self.cfg, lambda servers: None)
        self.assertFalse(any(a.isChecked() for a in restored.server_actions))
        restored.close()
