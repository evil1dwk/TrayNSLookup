import csv
import io
import json
import unittest
from traynslookup.result_tools import export_result, history_matches, RECORD_TYPES


def fixture():
    return dict(query='example.com', timestamp='2026-10-25 09:00:00', comparison='', results=[
        dict(requested_server='1.1.1.1', server='1.1.1.1', elapsed_ms=4.5, record_type='TXT', error='', records=[
            dict(name='example.com.', type='TXT', value='"hello, world\\nnext"', ttl=60)]),
        dict(requested_server='8.8.8.8', server='', elapsed_ms=5000, record_type='TXT', error='Timeout', records=[])])


class ResultToolsTests(unittest.TestCase):
    def test_exports_preserve_records_metadata_and_errors(self):
        lookup = fixture()
        self.assertEqual(json.loads(export_result(lookup, '', 'json')), lookup)
        rows = list(csv.DictReader(io.StringIO(export_result(lookup, '', 'csv'))))
        self.assertEqual(rows[0]['value'], lookup['results'][0]['records'][0]['value'])
        self.assertEqual(rows[0]['ttl'], '60')
        self.assertEqual(rows[0]['timestamp'], lookup['timestamp'])
        self.assertEqual(rows[1]['error'], 'Timeout')
        self.assertIn('Timeout', export_result(lookup, '', 'txt'))

    def test_legacy_export_is_lossless(self):
        text = 'saved, result\nwith multiple lines'
        self.assertEqual(export_result(None, text, 'txt'), text)
        self.assertEqual(json.loads(export_result(None, text, 'json')), {'result': text})
        self.assertEqual(list(csv.DictReader(io.StringIO(export_result(None, text, 'csv')))), [{'result': text}])

    def test_combined_history_filters_and_inclusive_dates(self):
        lookup = fixture()
        entry = dict(query=lookup['query'], lookup=lookup, result='old text')
        self.assertTrue(history_matches(entry, 'EXAMPLE', '1.1', 'TXT', '2026-10-25', '2026-10-25'))
        for kwargs in [dict(query='other'), dict(server='9.9'), dict(record_type='A'),
                       dict(start='2026-10-26'), dict(end='2026-10-24')]:
            self.assertFalse(history_matches(entry, **kwargs))
        self.assertTrue(history_matches(entry, server='8.8.8.8'))

    def test_legacy_date_search_and_unknown_metadata(self):
        entry = dict(query='example.com', result='2026-10-25 09:00:00\nsaved result')
        self.assertTrue(history_matches(entry, query='example', start='2026-10-25'))
        self.assertFalse(history_matches(entry, record_type='A'))
        entry['result'] = 'no timestamp'
        self.assertFalse(history_matches(entry, start='2026-10-25'))

    def test_record_types(self):
        self.assertTrue({'SOA', 'SRV', 'CAA', 'HTTPS'}.issubset(RECORD_TYPES))
