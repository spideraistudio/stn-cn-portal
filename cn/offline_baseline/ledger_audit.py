"""Read-only, period-scoped ledger checks. No calculation or issue writes."""
import copy, hashlib, json, re
from collections import defaultdict, Counter
from datetime import date
from decimal import Decimal


def norm(value):
    return re.sub(r'\s+', ' ', str(value or '')).strip().upper()


def number(value):
    n = Decimal(str(value or 0))
    if not n.is_finite():
        raise ValueError('Invalid numeric source value')
    return n


def narration(entry):
    lines = [norm(x.get('text')) for x in entry.get('source_lines', [])[1:]]
    # Exclude allocation/cheque details and print totals. Keep descriptions with quantities; these can identify CN benefits.
    lines = [x for x in lines if x and not re.match(
        r'^(?:AGST REF|NEW REF|CHEQUE/DD|AVAILABLE ONLY|CONTINUED|BROUGHT FORWARD|CARRIED OVER)', x)
]
    return ' '.join(lines) or norm(entry.get('remarks'))


def bank_reference(text):
    # Require a concrete transfer identifier containing digits; NEFT alone is not evidence.
    match = re.search(r'\b(?:NEFT|RTGS|IMPS|UPI)[\s:/-]+([A-Z0-9]{6,})\b', text)
    return match[1] if match and re.search(r'\d', match[1]) else None


def voucher_view(doc, entry):
    v={'party': doc.get('party', ''), 'location': doc.get('location', ''),
            'filename': doc.get('audit_filename', 'Statement.pdf'),
            'date': entry.get('date'), 'reference': entry.get('reference'),
            'kind': entry.get('kind'), 'debit': entry.get('debit', '0'),
            'credit': entry.get('credit', '0'), 'narration': narration(entry),
            'source_lines': copy.deepcopy(entry.get('source_lines', [])),
            'items': copy.deepcopy(entry.get('items', []))}
    v['product_mapping_key']=cn_product_key(v)
    return v

def cn_product_key(view):
    return finding_id({'type':'Posted CN product attribution','vouchers':[view]},'','')


def strict_return_item(item):
    """Only complete positive source lines qualify; never guess a missing value."""
    name, unit = norm(item.get('name')), norm(item.get('unit'))
    if not name or not unit or any(item.get(k) in (None, '') for k in ('qty', 'amount')):
        return None
    qty, amount = number(item['qty']), number(item['amount'])
    if qty <= 0 or amount <= 0:
        return None
    # Source names retain packing variants (including DAWAT). Explicit source
    # packing, when present, must match too. Catalogue suggestions are not proof.
    packing = item.get('packing_kg')
    packing = str(number(packing).normalize()) if packing not in (None, '') else ''
    return (name, unit, packing, qty, amount)


def cross_party_returns(entries, flag):
    matches = defaultdict(list)
    for identity, doc, entry in entries:
        if entry.get('kind') != 'return':
            continue
        items = entry.get('items', [])
        signatures = [strict_return_item(item) for item in items]
        complete = bool(signatures) and all(key is not None for key in signatures)
        full = (Counter(signatures), number(entry.get('credit')), number(entry.get('debit'))) if complete else None
        # One voucher per group, even when its printed item repeats. Keep all
        # matching source lines rather than making a voucher duplicate itself.
        grouped = defaultdict(list)
        for item, key in zip(items, signatures):
            if key is not None:
                grouped[key].append(copy.deepcopy(item))
        for key, lines in grouped.items():
            view = voucher_view(doc, entry)
            view['item'] = lines[0]
            view['matching_items'] = lines
            matches[(entry['date'], key)].append((identity, view, full))
    for (day, key), rows in matches.items():
        if len({identity for identity, _, _ in rows}) < 2:
            continue
        full_match = all(full is not None and full == rows[0][2] for _, _, full in rows)
        name, unit, packing, qty, amount = key
        flag('Possible duplicate sales return',
             'Different parties have a sales return with the same posting date, exact source product/packing, unit, quantity and item amount. Review both entries; an exact match can still be legitimate. No entries have been changed.',
             [view for _, view, _ in rows], product=name, unit=unit,
             quantity=qty, return_amount=amount, matching_date=day,
             full_voucher_match=full_match,
             evidence=f'{day} | {name} | {unit} | {qty} | item amount {amount}' + (f' | packing {packing} kg' if packing else ''))


def finding_id(finding, start, end):
    """Bind review to the period and exact financial evidence, not upload filename."""
    vouchers = []
    for v in finding.get('vouchers', []):
        vouchers.append({'party':norm(v.get('party')), 'location':norm(v.get('location')),
                         'date':v.get('date'), 'reference':norm(v.get('reference')),
                         'kind':v.get('kind'), 'debit':str(number(v.get('debit')).normalize()),
                         'credit':str(number(v.get('credit')).normalize()), 'narration':norm(v.get('narration')),
                         'items':sorted([(norm(i.get('name')),norm(i.get('unit')),
                                         str(number(i.get('qty')).normalize()),str(number(i.get('amount')).normalize()),
                                         str(number(i.get('rate')).normalize()),str(i.get('packing_kg','')))
                                        for i in v.get('items',[])])})
    evidence = [start,end,finding.get('type'),norm(finding.get('product')),norm(finding.get('unit')),
                str(finding.get('evidence','')),sorted(vouchers,key=lambda v:json.dumps(v,sort_keys=True))]
    return hashlib.sha256(json.dumps(evidence,sort_keys=True,default=str).encode()).hexdigest()


def save_audit_review(store, payload):
    from datetime import datetime, timezone
    cfg=store.settings()
    if payload.get('version')!=cfg['version']:
        raise ValueError('Settings changed; refresh and review again')
    start,end=payload.get('start'),payload.get('end')
    if not start or not end or date.fromisoformat(start)>date.fromisoformat(end):
        raise ValueError('Choose a valid audit period')
    finding=payload.get('finding',{})
    if not finding.get('type') or not finding.get('vouchers'):
        raise ValueError('Finding evidence is required')
    key=finding_id(finding,start,end)
    if key!=payload.get('review_id'):
        raise ValueError('Finding evidence changed; run the audit again')
    reviews=cfg.setdefault('audit_finding_reviews',{})
    if payload.get('reset'):
        reviews.pop(key,None)
    else:
        reason=str(payload.get('reason','')).strip()
        if not reason:raise ValueError('Enter why this finding is not applicable')
        reviews[key]={'status':'not_applicable','reason':reason,'reviewed_at':datetime.now(timezone.utc).isoformat(),
                      'type':finding['type'],'start':start,'end':end}
    return store.save_settings(cfg)


def cn_classification(view, settings):
    text=view['narration'];settings=settings or {}
    saved=settings.get('audit_cn_classifications',{}).get(text)
    if saved:return saved
    if text in settings.get('audit_crop_mappings',{}):return 'scheme'
    if re.search(r'\b(?:FREIGHT|TRANSPORT|TRANSPORTATION|COURIER)\b',text):return 'freight'
    return 'unclassified'


def audit_documents(documents, start, end, settings=None):
    if not start or not end or date.fromisoformat(start) > date.fromisoformat(end):
        raise ValueError('Choose a valid checking period: start must be on or before end')
    products = {p['id']: p for p in (settings or {}).get('products', [])}
    warnings, findings, posted, entries, stock_timing = [], [], [], [], []
    # Multiset union: overlapping PDFs do not create a duplicate, but two printed
    # identical postings in ONE ledger are retained as two distinct occurrences.
    seen = Counter()
    parties = set()
    for doc in documents:
        if doc.get('import_error'):
            warnings.append({'party': doc.get('party', ''), 'message': doc['import_error']})
            continue
        identity = (norm(doc.get('party')), norm(doc.get('location')))
        parties.add(identity)
        warnings.extend({'party': doc.get('party', ''), 'message': w} for w in doc.get('warnings', []))
        local = Counter()
        for entry in doc.get('entries', []):
            if not entry.get('date') or not start <= entry['date'] <= end:
                continue
            stable = [identity, entry.get('date'), entry.get('reference'),
                      entry.get('kind'), str(number(entry.get('debit')).normalize()), str(number(entry.get('credit')).normalize()),
                      [(norm(i.get('name')), i.get('unit'), str(number(i.get('qty')).normalize()), str(number(i.get('rate')).normalize()), str(number(i.get('amount')).normalize())) for i in entry.get('items', [])]]
            key = json.dumps(stable, sort_keys=True)
            local[key] += 1
            if local[key] > seen[key]:
                entries.append((identity, doc, entry))
        for key, count in local.items():
            seen[key] = max(seen[key], count)
    def flag(kind, message, vouchers, **extra):
        findings.append({'type': kind, 'message': message, 'vouchers': vouchers, **extra})
    payments, cns = defaultdict(list), defaultdict(list)
    for identity, doc, entry in entries:
        view = voucher_view(doc, entry)
        text = view['narration']
        if entry['kind'] == 'receipt':
            bank = bank_reference(text)
            if bank:
                payments[('bank reference', bank)].append(view)
            elif len(text) >= 12 and re.search(r'\d', text):
                # Exact narration may also catch non-NEFT references. Generic labels
                # and equal payment amounts never trigger a warning.
                payments[('exact narration', text)].append(view)
        elif entry['kind'] == 'posted_cn':
            crops = sorted({p['crop'] for p in products.values() if any(norm(label) and re.search(r'\b'+re.escape(norm(label))+r'\b', text) for label in [p.get('crop'),p.get('name')]+p.get('aliases',[]))})
            view['mapping_key']=text
            view['crop']=(settings or {}).get('audit_crop_mappings',{}).get(text) or ', '.join(crops) or 'Not identifiable from narration'
            view['cn_classification']=cn_classification(view,settings)
            if view['cn_classification']=='freight':view['crop']='Freight / transport CN — no crop mapping'
            elif view['cn_classification']=='other':view['crop']='Other adjustment — no crop mapping'
            posted.append(view)
            # Nonempty descriptive narration, same party, same amount. A same-amount
            # CN with a different narration is deliberately never grouped.
            if len(text) >= 12 and re.search(r'[A-Z]', text) and text not in ('CREDIT NOTE', 'CREDIT NOTE GIVEN', 'CN GIVEN', 'DISCOUNT GIVEN'):
                cns[(identity, text, str(number(entry.get('credit')).normalize()))].append(view)
    for (evidence, reference), rows in payments.items():
        if len(rows) > 1:
            flag('Duplicate payment reference', 'Separate payment vouchers share '+evidence+'. Review against the bank record; amounts alone are never used.', rows, evidence=reference)
    for (_, text, _), rows in cns.items():
        if len(rows) > 1:
            flag('Possible duplicate CN', 'Separate CN vouchers for this party share the complete narration and credit amount. Confirm whether both were intended.', rows, evidence=text)
    cross_party_returns(entries, flag)
    by_party = defaultdict(list)
    for identity, doc, entry in entries:
        by_party[identity].append((doc, entry))
    for party_entries in by_party.values():
        supplies = defaultdict(list)
        coverage=defaultdict(lambda:{'supply':Decimal(0),'returned':Decimal(0),'ipt':Decimal(0),'vouchers':[]})
        for coverage_doc,coverage_entry in party_entries:
            if coverage_entry['kind'] not in ('sale','return','ipt_in','ipt_out'):continue
            for item in coverage_entry.get('items',[]):
                key=(norm(item.get('name')),item.get('unit'));row=coverage[key];quantity=number(item.get('qty'))
                row['vouchers'].append({**voucher_view(coverage_doc,coverage_entry),'item':copy.deepcopy(item)})
                if coverage_entry['kind']=='return':row['returned']+=quantity
                else:row['supply']+=quantity*(-1 if coverage_entry['kind']=='ipt_out' else 1)
                if coverage_entry['kind']=='ipt_in':row['ipt']+=quantity
        for (name,unit),row in coverage.items():
            if row['returned']>max(Decimal(0),row['supply']):
                flag('Return supply needs review','Returns exceed supply + IPT received - IPT given over the complete selected period; entry order alone is not treated as missing supply.',row['vouchers'],product=name,unit=unit,quantity=row['returned'],net_supply=row['supply'])
        for doc, entry in sorted(party_entries, key=lambda pair: (pair[1]['date'], pair[1]['kind'] != 'sale')):
            if entry['kind'] not in ('sale', 'return', 'ipt_in', 'ipt_out'):
                continue
            for item in entry.get('items', []):
                # Exact source item name and unit preserve pack/DAWAT identity.
                key = (norm(item.get('name')), item.get('unit'))
                qty, rate = number(item.get('qty')), number(item.get('rate'))
                if qty <= 0 or rate <= 0:
                    continue
                view = {**voucher_view(doc, entry), 'item': copy.deepcopy(item)}
                if entry['kind'] == 'sale':
                    supplies[key].append((rate, qty, view))
                elif entry['kind'] == 'return':
                    prior = supplies[key]
                    if not prior:
                        covered=coverage[key]['supply']>=coverage[key]['returned']
                        stock_timing.append({'party':doc.get('party',''),'product':item['name'],'message':('Complete-period stock covers this return, including any later IPT. No earlier invoice rate is available; no return-rate excess is assumed.' if covered else 'No earlier invoice rate is available. Review full-period stock coverage and any IPT posted outside the checking period; no rate excess is assumed.'),'vouchers':coverage[key]['vouchers']})
                        continue
                    low, high = min(r[0] for r in prior), max(r[0] for r in prior)
                    if rate > low:
                        definite = rate > high
                        flag('Return rate above supply' if definite else 'Mixed supply rates — review return',
                             'Return rate exceeds every earlier matching supply rate in this period.' if definite else 'Multiple earlier supply rates exist. The return exceeds the lowest rate; identify its original invoice before concluding an error.',
                             [r[2] for r in prior]+[view], product=item['name'], unit=item['unit'], quantity=qty,
                             return_rate=rate, supply_rate_min=low, supply_rate_max=high,
                             possible_excess_min=qty*max(Decimal(0),rate-high), possible_excess_max=qty*(rate-low),
                             invoice_match_confirmed=False)
    for finding in findings:
        finding['review_id']=finding_id(finding,start,end)
        finding['review']=copy.deepcopy((settings or {}).get('audit_finding_reviews',{}).get(finding['review_id']))
    warnings = list({(w['party'], w['message']): w for w in warnings}.values())
    from ledger_nrv import build,mark_incomplete
    nrv=build(entries,settings)
    if any(d.get('import_error') or d.get('warnings') for d in documents):mark_incomplete(nrv,'Some source ledgers have parsing/coverage warnings; combined crop/product averages are withheld')
    return {'posted_CN_NRV':nrv,'start': start, 'end': end, 'party_count': len(parties), 'voucher_count': len(entries),
            'posted_CNs': posted, 'findings': findings, 'warnings': warnings, 'stock_timing':stock_timing,
            'notes': ['Read-only checks; no CN calculation, allocation or ledger entry is changed.',
                      'Payment duplicates require transaction-reference or exact descriptive narration evidence, never equal amounts alone.',
                      'Cross-party sales returns require the same date, exact source product/packing, unit, positive quantity and positive item amount. No weaker-match warnings; complete-voucher matches are identified separately.',
                      'Rate checks use earlier printed supply rates within the selected period and exact source product/packing names and units. They do not infer FIFO or identify an original invoice.',
                      'IPT is excluded from supply-rate comparisons. Missing or differently named supply, prior returns, transfers and quantity availability require review; displayed excess is a rate comparison, not an approved recovery.']}
