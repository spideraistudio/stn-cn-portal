"""Draft-only review gates derived from canonical statement evidence."""
PREFIX = 'Incomplete item statement review: '
FORMATS = {'tally-balance-columns-v1', 'account-compact-v1', 'account-item-detail-v1'}


def project_reviews(record, document):
    if document.get('source', {}).get('format') not in FORMATS:
        return record
    warnings = [w for w in record.get('import_warnings', []) if not w.startswith(PREFIX)]
    warnings.extend(w for w in document.get('warnings', []) if w not in warnings)
    def flag(message):
        warnings.append(PREFIX + message)
    def reason(value):
        return isinstance(value, str) and len(value.strip()) >= 5
    if document['source'].get('opening_omitted_zero') and not reason(record.get('opening_review_reason')):
        flag('Confirm the unprinted zero opening balance in Check Ledger with a reason.')
    current = {e['id']: e for e in record.get('entries', [])}
    for original in document['entries']:
        entry = current.get(original['id'])
        if not entry:
            flag('Source voucher missing: ' + original['reference']); continue
        items = entry.get('items', [])
        for index, source_item in enumerate(original.get('items', [])):
            if index >= len(items):
                flag(original['reference'] + ': source item missing'); continue
            item = items[index]
            if source_item.get('unit') == 'unknown' and (item.get('unit') not in ('kg','packet') or not reason(item.get('unit_review_reason'))):
                flag(original['reference'] + ': confirm quantity unit and reason for ' + source_item['name'])
        if any(i.get('amount_basis') == 'calculated_qty_times_rate' for i in original.get('items', [])) and not reason(entry.get('amount_review_reason')):
            flag(original['reference'] + ': verify working item amounts against invoice and enter an amount review reason.')
    record['import_warnings'] = list(dict.fromkeys(warnings))
    return record


def same_issuer(a, b):
    left = a.get('source', {}).get('issuer', '').strip().casefold()
    right = b.get('source', {}).get('issuer', '').strip().casefold()
    return not (left or right) or left == right


def analyse_pair(previous, current, *args, **kwargs):
    from year_link import analyse_pair as legacy_pair
    if not same_issuer(previous, current):
        raise ValueError('Year Link requires statements from the same issuing company')
    return legacy_pair(previous, current, *args, **kwargs)
