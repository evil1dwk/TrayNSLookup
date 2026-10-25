from copy import deepcopy
import unittest
from traynslookup.comparisons import server_statuses, compare_history
from traynslookup.result_tools import export_result
from test_result_tools import fixture


class ComparisonTests(unittest.TestCase):
    def test_resolver_highlights_shared_and_different_and_failures(self):
        lookup = fixture()
        a = lookup['results'][0]
        b = deepcopy(a)
        self.assertEqual(server_statuses([a, b]), [['Shared'], ['Shared']])
        b['records'][0]['value'] = 'changed'
        self.assertEqual(server_statuses([a, b]), [['Different'], ['Different']])
        b['error'] = 'timeout'
        self.assertEqual(server_statuses([a, b]), [['Unable to compare'], ['Unable to compare']])

    def test_history_diff_ignores_ttl_and_preserves_baseline(self):
        saved = fixture()
        saved['results'] = saved['results'][:1]
        current = deepcopy(saved)
        original = deepcopy(saved)
        current['results'][0]['records'][0]['ttl'] = 90
        diff = compare_history(saved, current)
        self.assertEqual(diff['results'][0]['rows'][0]['status'], 'Unchanged')
        current['results'][0]['records'][0]['value'] = 'new value'
        diff = compare_history(saved, current)
        self.assertEqual({r['status'] for r in diff['results'][0]['rows']}, {'Added', 'Removed'})
        self.assertEqual(saved, original)
        current['history_comparison'] = diff
        self.assertIn('Removed', export_result(current, '', 'csv'))
        self.assertIn('Saved:', export_result(current, '', 'txt'))

    def test_failure_or_changed_system_resolver_never_means_removed(self):
        saved = fixture()
        current = deepcopy(saved)
        current['results'][0]['error'] = 'timeout'
        diff = compare_history(saved, current)
        self.assertEqual(diff['results'][0]['rows'], [])
        self.assertTrue(diff['results'][0]['error'])
        saved['results'][0]['requested_server'] = 'System default'
        current = deepcopy(saved)
        current['results'][0]['server'] = '9.9.9.9'
        self.assertIn('different', compare_history(saved, current)['results'][0]['error'])
