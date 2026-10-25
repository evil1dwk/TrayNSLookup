"""DNS queries and serializable results, shared by single and comparison lookups."""
from concurrent.futures import ThreadPoolExecutor
import ipaddress
from time import perf_counter

import dns.rdatatype
import dns.resolver
from PyQt6.QtCore import QThread, pyqtSignal


def prepare_query(query, record_type):
    query = query.strip()
    try:
        address = ipaddress.ip_address(query)
    except ValueError:
        return query, record_type
    return address.reverse_pointer + '.', 'PTR'


def lookup_server(query, record_type, server):
    name, kind = prepare_query(query, record_type)
    result = dict(query=query, name=name, record_type=kind,
                  requested_server=server or 'System default', server=server or '',
                  records=[], error='', elapsed_ms=0)
    started = perf_counter()
    try:
        # Explicit resolvers must also work when the OS has no DNS configuration.
        resolver = dns.resolver.Resolver(configure=server is None)
        if server:
            resolver.nameservers = [server]
        resolver.lifetime = 5
        resolver.timeout = 3
        answer = resolver.resolve(name, kind, search=False)
        result['server'] = str(answer.nameserver or server or 'System default')
        for rrset in answer.response.answer:
            for record in rrset:
                result['records'].append(dict(name=rrset.name.to_text(),
                    type=dns.rdatatype.to_text(rrset.rdtype), value=record.to_text(), ttl=rrset.ttl))
    except Exception as exc:
        result['error'] = f'{type(exc).__name__}: {exc}'
    result['elapsed_ms'] = round((perf_counter() - started) * 1000, 2)
    return result


def comparison_summary(results):
    if len(results) < 2:
        return ''
    if any(r['error'] for r in results):
        return 'Comparison incomplete: one or more servers failed.'
    # TTLs and answer order vary normally; compare names, types and values only.
    signatures = [{(r['name'].lower(), r['type'], r['value']) for r in item['records']}
                  for item in results]
    return ('Answers match (ignoring TTL and order).' if all(s == signatures[0] for s in signatures)
            else 'Answers differ between servers.')


class DNSLookupThread(QThread):
    completed = pyqtSignal(object)

    def __init__(self, query, record_type, servers):
        super().__init__()
        self.query = query
        self.record_type = record_type
        self.servers = servers if isinstance(servers, list) else [servers]

    def run(self):
        with ThreadPoolExecutor(max_workers=min(8, max(1, len(self.servers)))) as pool:
            results = list(pool.map(lambda server: lookup_server(
                self.query, self.record_type, server), self.servers))
        self.completed.emit(dict(query=self.query, results=results,
                                 comparison=comparison_summary(results)))
