import ipaddress
import unittest
from unittest.mock import patch, Mock
import dns.message
import dns.rrset
from traynslookup.dns_worker import prepare_query, lookup_server, comparison_summary, DNSLookupThread


def answer_fixture(value='192.0.2.1', ttl=60):
    query = dns.message.make_query('example.com.', 'A')
    response = dns.message.make_response(query)
    response.answer.append(dns.rrset.from_text('example.com.', ttl, 'IN', 'A', value))
    return Mock(response=response, nameserver='1.1.1.1')


class DNSTests(unittest.TestCase):
    def test_reverse_ipv4_ipv6_and_regular_names(self):
        for address in ('192.0.2.1', '2001:db8::1'):
            self.assertEqual(prepare_query(address, 'A'), (ipaddress.ip_address(address).reverse_pointer + '.', 'PTR'))
        self.assertEqual(prepare_query(' example.com ', 'MX'), ('example.com', 'MX'))
        self.assertEqual(prepare_query('1.2.0.192.in-addr.arpa.', 'PTR'), ('1.2.0.192.in-addr.arpa.', 'PTR'))

    def test_structured_answers_include_cname_ttl_server_and_time(self):
        answer = answer_fixture()
        answer.response.answer.insert(0, dns.rrset.from_text('alias.example.', 120, 'IN', 'CNAME', 'example.com.'))
        with patch('traynslookup.dns_worker.dns.resolver.Resolver') as factory:
            factory.return_value.resolve.return_value = answer
            result = lookup_server('example.com', 'A', '1.1.1.1')
            factory.assert_called_once_with(configure=False)
            factory.return_value.resolve.assert_called_once_with('example.com', 'A', search=False)
        self.assertFalse(result['error'])
        self.assertEqual(result['records'][0]['type'], 'CNAME')
        self.assertEqual(result['records'][1]['ttl'], 60)
        self.assertEqual(result['server'], '1.1.1.1')
        self.assertGreaterEqual(result['elapsed_ms'], 0)

    def test_errors_including_resolver_setup_are_returned(self):
        with patch('traynslookup.dns_worker.dns.resolver.Resolver', side_effect=RuntimeError('no resolver')):
            self.assertIn('no resolver', lookup_server('example.com', 'A', None)['error'])
        with patch('traynslookup.dns_worker.dns.resolver.Resolver') as factory:
            factory.return_value.resolve.side_effect = TimeoutError('timed out')
            self.assertIn('TimeoutError', lookup_server('example.com', 'A', '1.1.1.1')['error'])

    def test_matching_different_and_failed_comparisons(self):
        a = dict(error='', records=[dict(name='example.com.', type='A', value='192.0.2.1', ttl=30)])
        b = dict(error='', records=[dict(name='EXAMPLE.COM.', type='A', value='192.0.2.1', ttl=60)])
        self.assertIn('match', comparison_summary([a, b]))
        b['records'][0]['value'] = '192.0.2.2'
        self.assertIn('differ', comparison_summary([a, b]))
        b['error'] = 'timeout'
        self.assertIn('incomplete', comparison_summary([a, b]))

    def test_worker_preserves_server_order_and_partial_failure(self):
        worker = DNSLookupThread('example.com', 'A', ['1.1.1.1', '8.8.8.8'])
        received = []
        worker.completed.connect(received.append)
        def lookup(query, kind, server):
            return dict(error='timeout' if server == '8.8.8.8' else '', records=[], server=server)
        with patch('traynslookup.dns_worker.lookup_server', side_effect=lookup):
            worker.run()
        self.assertEqual([r['server'] for r in received[0]['results']], ['1.1.1.1', '8.8.8.8'])
        self.assertIn('incomplete', received[0]['comparison'])
