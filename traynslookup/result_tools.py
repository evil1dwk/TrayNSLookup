"""Formatting, exporting and filtering saved DNS results without GUI dependencies."""
import csv
import io
import json

RECORD_TYPES = ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS', 'PTR', 'SOA', 'SRV', 'CAA', 'HTTPS']
FIELDS = ['query', 'query_type', 'timestamp', 'requested_server', 'server', 'elapsed_ms',
          'name', 'type', 'value', 'ttl', 'error']


def result_rows(lookup):
    rows = []
    for result in lookup['results']:
        base = {key: result.get(key, '') for key in ('requested_server', 'server', 'elapsed_ms', 'error')}
        base.update(query=lookup['query'], query_type=result.get('record_type', ''), timestamp=lookup.get('timestamp', ''))
        for record in result['records'] or [{}]:
            rows.append({**base, **{key: record.get(key, '') for key in ('name', 'type', 'value', 'ttl')}})
    return rows


def format_text(lookup):
    lines = [lookup.get('timestamp', ''), f"Query: {lookup['query']}", lookup.get('comparison', '')]
    for result in lookup['results']:
        lines.append(f"{result['requested_server']} — {result['server']} ({result['elapsed_ms']} ms)")
        lines.append(result['error'] or '\n'.join(
            f"{r['name']} {r['ttl']} {r['type']} {r['value']}" for r in result['records']))
    return '\n'.join(lines).strip()


def export_result(lookup, legacy_text, kind):
    if kind == 'json':
        return json.dumps(lookup if lookup is not None else {'result': legacy_text}, indent=2, ensure_ascii=False)
    if kind == 'csv':
        output = io.StringIO(newline='')
        # Older results do not contain parsed records; preserve their full text.
        fields = FIELDS if lookup is not None else ['result']
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(result_rows(lookup) if lookup is not None else [{'result': legacy_text}])
        return output.getvalue()
    return format_text(lookup) if lookup is not None else legacy_text


def history_matches(entry, query='', server='', record_type='', start='', end=''):
    if query.casefold() not in entry.get('query', '').casefold():
        return False
    lookup = entry.get('lookup', {})
    results = lookup.get('results', [])
    if record_type and not any(r.get('record_type') == record_type for r in results):
        return False
    if server and not any(server.casefold() in str(r.get(key, '')).casefold()
                          for r in results for key in ('requested_server', 'server')):
        return False
    if start or end:
        stamp = entry.get('timestamp') or lookup.get('timestamp') or entry.get('result', '').split('\n')[0]
        day = stamp[:10]
        from datetime import date
        try:
            date.fromisoformat(day)
        except ValueError:
            return False
        if (start and day < start) or (end and day > end):
            return False
    return True
