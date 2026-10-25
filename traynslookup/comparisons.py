"""Record comparisons ignore TTL and answer order, and retain explicit status labels."""
def record_key(record):
    return record['name'].casefold(), record['type'], record['value']


def server_statuses(results):
    if len(results) < 2:
        return [[''] * len(r['records']) for r in results]
    if any(r['error'] for r in results):
        return [['Unable to compare'] * len(r['records']) for r in results]
    sets = [{record_key(record) for record in r['records']} for r in results]
    shared = set.intersection(*sets)
    return [['Shared' if record_key(record) in shared else 'Different' for record in r['records']]
            for r in results]


def compare_history(saved, current):
    previous = {r['requested_server']: r for r in saved['results']}
    results = []
    for result in current['results']:
        old = previous.get(result['requested_server'])
        reason = ''
        if old is None or old.get('record_type') != result.get('record_type'):
            reason = 'No matching saved query for this server.'
        elif old['error'] or result['error']:
            reason = 'Saved or current lookup failed; records cannot be compared.'
        elif result['requested_server'] == 'System default' and old['server'] != result['server']:
            reason = 'System default used a different responding resolver.'
        rows = []
        if not reason:
            before = {record_key(r): r for r in old['records']}
            after = {record_key(r): r for r in result['records']}
            for key in sorted(before.keys() | after.keys()):
                record = dict(after.get(key) or before[key])
                record.update(status='Unchanged' if key in before and key in after else
                              'Added' if key in after else 'Removed',
                              saved_ttl=before.get(key, {}).get('ttl', ''),
                              current_ttl=after.get(key, {}).get('ttl', ''))
                rows.append(record)
        results.append(dict(requested_server=result['requested_server'], rows=rows, error=reason))
    return dict(saved_timestamp=saved.get('timestamp', 'Unknown'),
                current_timestamp=current.get('timestamp', 'Unknown'), results=results)
