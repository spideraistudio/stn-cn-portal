"""Workbook-local product identity resolution; never derives financial settings."""
import re
from decimal import Decimal

from importer import product_suggestion


def name_key(name):
    return ' '.join(name.casefold().split())


def packing(item):
    # Use the preserved parser's interpretation of the PRINTED name, rather
    # than trusting a selected catalogue packing or a browser field.
    pack = product_suggestion(item['name'], {'products': []})['detected_packing_kg']
    grams = re.search(r'(\d+(?:\.\d+)?)\s*(?:grms?|grams?)\b', item['name'], re.I)
    return pack if pack is not None else str(Decimal(grams[1])/1000) if grams else None


def identity(item):
    pack = packing(item)
    return (name_key(item['name']), item['unit'], str(Decimal(pack).normalize()) if pack else None)


def compatible(item, product):
    pack = packing(item)
    return pack is None or Decimal(pack) == Decimal(product['packing_kg'])


def remembered(state):
    choices = {}
    for ledger in state['ledgers']:
        if ledger['superseded_by']:
            continue
        for ei, entry in enumerate(ledger['document']['entries']):
            for ii, item in enumerate(entry.get('items', [])):
                pid = ledger['mappings'].get(f'{ei}:{ii}')
                if pid:
                    choices.setdefault(identity(item), set()).add(pid)
    return choices


def resolve(item, state, saved):
    products = {p['id']: p for p in state['catalogue']}
    prior = saved.get(identity(item), set())
    if prior:
        if len(prior) == 1:
            pid = next(iter(prior))
            if pid in products and compatible(item, products[pid]):
                return pid, 'Saved workbook mapping'
        return None, 'Conflicting saved mappings; choose the correct product and packing'
    # Keep Update35.2 name/packing recognition, but do not auto-select a broad
    # substring match (e.g. a new "LEGEND PLUS" against existing "LEGEND").
    hint = product_suggestion(item['name'], {'products': state['catalogue']})
    pid = hint['product']
    if pid:
        p = products[pid]
        def bare(value):
            return name_key(re.sub(r'\b\d+(?:\.\d+)?\s*(?:kgs?|gms?|g)\b', '', value, flags=re.I))
        aliases = [p['name'], *p.get('aliases', [])]
        if any(name_key(a) == name_key(item['name']) or
               packing(item) is not None and bare(a) == bare(item['name']) for a in aliases):
            return pid, 'Recognised workbook product and packing'
    return None, hint['reason'] if not pid else 'New printed name; confirm the suggested product'


def plan(document, state):
    saved = remembered(state)
    result = {}
    for ei, entry in enumerate(document['entries']):
        for ii, item in enumerate(entry.get('items', [])):
            pid, reason = resolve(item, state, saved)
            result[f'{ei}:{ii}'] = {'product_id': pid, 'reason': reason}
    return result
