"""Phase 4 owned ledger adapter. Uses preserved, stateless Update35.2 functions.

No offline HTTP server or Store is mounted. Source originals are immutable;
review decisions, mappings and carry-forward evidence are separate draft data.
"""
import base64
import copy
from datetime import date
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import sys
import uuid

from .data_store import fields, identifier
from .security import AuthError, require_permission

BASELINE = Path(__file__).resolve().parents[2] / 'offline_baseline'
# Fixed application code path, never a request/user/data path.
if str(BASELINE) not in sys.path:
    sys.path.insert(0, str(BASELINE))
# Extended payment-source engine; original Update35.2 baseline remains unchanged.
FINANCIAL_RUNTIME=Path(__file__).resolve().parent/'financial_runtime'
if str(FINANCIAL_RUNTIME) not in sys.path:sys.path.insert(0,str(FINANCIAL_RUNTIME))
from importer import compare_import, source_content
from .statement_import import import_pdf_documents
from .product_mapping import plan as mapping_plan, identity as mapping_identity, compatible as packing_compatible
from ledger_audit import audit_documents, narration
from year_link import attach_link, signature
from .statement_review import analyse_pair, same_issuer


def encode(value):
    return json.dumps(value, default=lambda x: str(x) if isinstance(x, Decimal) else x,
                      allow_nan=False, ensure_ascii=False, sort_keys=True)


def digest(value):
    return hashlib.sha256(encode(value).encode()).hexdigest()


def text(value, label='text', maximum=500, empty=False):
    if not isinstance(value, str) or len(value) > maximum or '\x00' in value or not empty and not value.strip():
        raise AuthError('Invalid '+label, 400)
    return value.strip()


def day(value):
    if not isinstance(value, str):
        raise AuthError('Choose an ISO date', 400)
    try:
        if date.fromisoformat(value).isoformat() != value:
            raise ValueError()
    except ValueError:
        raise AuthError('Choose an ISO date', 400) from None
    return value


def number(value):
    try:
        if type(value) not in (str, int):
            raise ValueError()
        n = Decimal(value)
        if not n.is_finite() or abs(n) > Decimal('1000000000000000'):
            raise ValueError()
        return n
    except (InvalidOperation, ValueError):
        raise AuthError('Invalid amount or quantity', 400) from None


def index(value, rows):
    if type(value) is not int or not 0 <= value < len(rows):
        raise AuthError('Source item not found', 404)
    return rows[value]


def empty_state():
    return {'catalogue': [], 'periods': [], 'ledgers': [], 'audit_reviews': {}, 'year_links': {}}


def validate_config(catalogue, periods, old=None):
    if not isinstance(catalogue, list) or len(catalogue) > 3000 or not isinstance(periods, list) or len(periods) > 100:
        raise AuthError('Invalid catalogue or periods', 400)
    seen = set()
    for p in catalogue:
        fields(p, {'id', 'name', 'crop', 'segment', 'packing_kg', 'aliases'})
        for k in ('id', 'name', 'crop', 'segment'):
            text(p[k], k, 200)
        if p['id'] in seen or number(p['packing_kg']) <= 0:
            raise AuthError('Duplicate product or invalid packing', 400)
        seen.add(p['id'])
        if not isinstance(p['aliases'], list) or len(p['aliases']) > 100:
            raise AuthError('Invalid aliases', 400)
        for a in p['aliases']:
            text(a, 'alias', 300)
    seen = set()
    for p in periods:
        fields(p, {'name', 'start', 'end', 'cutoff'})
        text(p['name'], 'period name', 100)
        if p['name'] in seen or not day(p['start']) <= day(p['end']) <= day(p['cutoff']):
            raise AuthError('Invalid or duplicate period', 400)
        seen.add(p['name'])
    for i,p in enumerate(periods):
        if any(max(q['start'], p['start']) <= min(q['end'], p['end']) for q in periods[i+1:]):
            raise AuthError('Working periods cannot overlap', 400)
    if old and old['ledgers']:
        # Never silently reinterpret saved mappings or season reviews.
        products = {p['id']: p for p in catalogue}
        for p in old['catalogue']:
            current = products.get(p['id'])
            if not current or any(current[k] != p[k] for k in ('crop', 'segment', 'packing_kg')):
                raise AuthError('Preserve existing product/packing identities; add a new product', 409)
        current = {p['name']: p for p in periods}
        for p in old['periods']:
            if current.get(p['name']) != p:
                raise AuthError('Preserve saved period dates; add another working period', 409)


class LedgerService:
    def __init__(self, store):
        self.store, self.accounts = store, store.accounts
        with self.accounts._tx() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS ledger_workspaces (
                owner TEXT NOT NULL, workbook TEXT NOT NULL, revision INTEGER NOT NULL,
                payload TEXT NOT NULL, PRIMARY KEY(owner,workbook))''')

    def load(self, db, owner, workbook):
        parent = self.store.row(db, owner, workbook, kind='workbooks')
        r = db.execute('SELECT revision,payload FROM ledger_workspaces WHERE owner=? AND workbook=?', (owner, workbook)).fetchone()
        return parent, (r['revision'] if r else 0), (json.loads(r['payload']) if r else empty_state())

    @staticmethod
    def expected(actual, supplied):
        if type(supplied) is not int or supplied != actual:
            raise AuthError('Workbook changed. Reload before saving or applying.', 409)

    def save(self, db, owner, workbook, revision, state, action, target=None):
        db.execute('INSERT OR REPLACE INTO ledger_workspaces VALUES(?,?,?,?)', (owner, workbook, revision+1, encode(state)))
        self.accounts.audit(db, owner, action, target or workbook)
        return revision+1

    @staticmethod
    def ledger(state, lid, active=True):
        identifier(lid)
        row = next((r for r in state['ledgers'] if r['id'] == lid), None)
        if not row or active and row.get('superseded_by'):
            raise AuthError('Ledger not found or replaced; reload the list', 404)
        return row

    @classmethod
    def current_source(cls, state, lid):
        row = cls.ledger(state, lid, False); seen = set()
        while row.get('superseded_by'):
            if row['id'] in seen: raise AuthError('Invalid statement replacement cycle', 400)
            seen.add(row['id']); row = cls.ledger(state, row['superseded_by'], False)
        return row

    @staticmethod
    def settings(state):
        return {'products': copy.deepcopy(state['catalogue']),
                'crops': sorted({p['crop'] for p in state['catalogue']})}

    @staticmethod
    def saved_choices(db, owner, workbook, state):
        products = list(state['catalogue']); schemes = []; crops = []
        if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='calculator_workspaces'").fetchone():
            row = db.execute('SELECT payload FROM calculator_workspaces WHERE owner=? AND workbook=?', (owner, workbook)).fetchone()
            if row:
                versions = json.loads(row['payload'])['settings']
                if versions:
                    cfg = json.loads(max(versions, key=lambda x: x[0])[1])
                    products += [p for p in cfg.get('products', []) if not p.get('deleted_at')]
                    schemes = [p for p in cfg.get('schemes', []) if not p.get('deleted_at') and not p.get('mapping_placeholder')]
                    crops += cfg.get('crops', [])
        def key(value): return ' '.join(value.split()).casefold()
        names = {}
        for value in [p['crop'] for p in products + schemes] + crops:
            if isinstance(value, str) and value.strip(): names.setdefault(key(value), ' '.join(value.split()))
        segments = {}
        for p in products + schemes:
            if p.get('segment') and p['segment'] != 'Awaiting scheme':
                crop = names[key(p['crop'])]
                segments.setdefault(crop, {}).setdefault(key(p['segment']), ' '.join(p['segment'].split()))
        return {'crops': sorted(names.values(), key=str.casefold),
                'segments': {c: sorted(v.values(), key=str.casefold) for c, v in segments.items()}}

    @staticmethod
    def effective(ledger, state):
        doc = copy.deepcopy(ledger['document'])
        products = {p['id']: p for p in state['catalogue']}
        for i, entry in enumerate(doc['entries']):
            review = ledger['reviews'].get(str(i), {})
            if 'kind' in review:
                entry['kind'] = review['kind']; entry['classification_required'] = False
            entry['web_review'] = copy.deepcopy(review)
            for j, item in enumerate(entry.get('items', [])):
                pid = ledger['mappings'].get(f'{i}:{j}')
                item['product'] = pid
                item['mapping_confirmed'] = bool(pid)
                if pid:
                    p = products[pid]
                    item.update(packing_kg=p['packing_kg'], crop=p['crop'], segment=p['segment'])
        resolved = {}
        for e in doc['entries']:
            for item in e.get('items', []):
                resolved[item['name']] = resolved.get(item['name'], True) and bool(item.get('product'))
        doc['warnings'] = [w for w in doc.get('warnings', []) if not (w.startswith('Map product/packing: ') and resolved.get(w[len('Map product/packing: '):], False))]
        return doc

    def state(self, token, workbook, ledger_id=None):
        with self.accounts._tx() as db:
            u = self.store.user(db, token)
            _, revision, s = self.load(db, u['id'], workbook)
            if ledger_id:
                r = self.ledger(s, ledger_id, False)
                return {'revision': revision, 'ledger': r, 'effective': self.effective(r, s),
                        'mapping_plan': mapping_plan(r['document'], s)}
            rows = []
            for r in s['ledgers']:
                doc = r['document']
                rows.append({k: r[k] for k in ('id', 'file_id', 'party_id', 'source_index', 'superseded_by')} | {
                    'party': doc['party'], 'location': doc.get('location', ''), 'entries': len(doc['entries']),
                    'report_period': list(self.report_period(doc)),
                    'opening': doc['opening'], 'closing': doc['closing'], 'reconciled': doc['reconciled'],
                    'warnings': doc.get('warnings', []), 'source_sha256': doc['source']['sha256']})
            return {**self.saved_choices(db, u['id'], workbook, s), 'revision': revision, 'catalogue': s['catalogue'], 'periods': s['periods'], 'ledgers': rows,
                    'year_links': {k: {'stale': self.link_stale(s, v), 'opening_sources': v['record']['opening_sources'],
                                      'review_note': v['record']['prior_year_link']['review_note']} for k, v in s['year_links'].items()}}

    def config(self, token, workbook, data):
        fields(data, {'revision'}, {'catalogue', 'periods'})
        if not set(data) & {'catalogue', 'periods'}:
            raise AuthError('Choose a configuration change', 400)
        with self.accounts._tx() as db:
            u = self.store.user(db, token, 'edit_ledger' if 'periods' in data else 'edit_schemes')
            if 'catalogue' in data: require_permission(u, 'edit_schemes')
            _, rev, s = self.load(db, u['id'], workbook)
            self.expected(rev, data['revision'])
            catalogue, periods = data.get('catalogue', s['catalogue']), data.get('periods', s['periods'])
            validate_config(catalogue, periods, s)
            s.update(catalogue=catalogue, periods=periods)
            return {'revision': self.save(db, u['id'], workbook, rev, s, 'ledger_config_saved')}

    @staticmethod
    def parse(raw, state):
        if not raw.startswith(b'%PDF-'):
            raise AuthError('Choose a text-based Tally PDF', 400)
        try:
            docs = import_pdf_documents(raw, LedgerService.settings(state))
            if not docs: raise ValueError('No party ledger found')
            for doc in docs:
                if doc.get('import_error'): raise ValueError('A party ledger could not be parsed: '+str(doc.get('party', '')))
                if not doc.get('party'): raise ValueError('Party not recognised')
                for e in doc['entries']: day(e['date'])
            return docs
        except (ValueError, ArithmeticError, KeyError) as exc:
            raise AuthError(str(exc), 400) from None

    def prepare(self, token, workbook, data):
        fields(data, {'revision', 'files'}, {'preview_digest', 'replacements', 'reason'})
        if not isinstance(data['files'], list) or not 1 <= len(data['files']) <= 30:
            raise AuthError('Select 1–30 PDF files per batch', 400)
        with self.accounts._tx() as db:
            u = self.store.user(db, token, 'import_statements'); require_permission(u, 'edit_ledger')
            parent, rev, s = self.load(db, u['id'], workbook); self.expected(rev, data['revision'])
            files = []
            for f in data['files']:
                if isinstance(f, dict) and set(f) == {'file_id'}:
                    r = self.store.row(db, u['id'], f['file_id'], kind='files')
                    if r['project'] != parent['project'] or r['workbook'] not in (None, workbook):
                        raise AuthError('Source file not found in this workbook/project', 404)
                    files.append({**json.loads(r['payload']), 'file_id': r['id'], 'file_revision': r['revision']})
                else:
                    fields(f, {'name', 'content_base64'}); text(f['name'], 'filename')
                    files.append(dict(f))
        # PDF work does not hold the account write lock. Reauthorization and
        # revision/linked-file checks happen again before any commit.
        parsed = []; seen = set()
        for fi, f in enumerate(files):
            try: raw = base64.b64decode(f['content_base64'], validate=True)
            except (ValueError, TypeError): raise AuthError('Invalid PDF bytes', 400) from None
            docs = self.parse(raw, s)
            for di, doc in enumerate(docs):
                key = f'{fi}:{di}'; source_key = (hashlib.sha256(raw).hexdigest(), di)
                if source_key in seen: continue
                seen.add(source_key)
                old = next((r for r in s['ledgers'] if not r['superseded_by'] and
                            r['file_sha256'] == source_key[0] and r['source_index'] == di), None)
                identity = (doc['party'].strip().casefold(), doc.get('location', '').strip().casefold())
                candidates = [r for r in s['ledgers'] if not r['superseded_by'] and
                              (r['document']['party'].strip().casefold(), r['document'].get('location', '').strip().casefold()) == identity
                              and same_issuer(r['document'],doc) and self.report_period(r['document']) == self.report_period(doc)]
                parsed.append({'key': key, 'file_index': fi, 'source_index': di, 'document': doc,
                               'file_sha256': source_key[0], 'existing_id': old['id'] if old else None,
                               'candidates': [r['id'] for r in candidates] if not old else []})
        identities = set()
        for p in parsed:
            doc = p['document']
            identity = (doc['party'].strip().casefold(), doc.get('location', '').strip().casefold(), doc.get('source',{}).get('issuer','').strip().casefold(), self.report_period(doc))
            if identity in identities:
                raise AuthError('Two different statements for the same party/period are in this batch. Import and review them in separate batches.', 409)
            identities.add(identity)
        fingerprint = digest({'workbook': workbook, 'revision': rev, 'files': files,
                              'documents': [(x['key'], x['file_sha256'], signature(x['document'])) for x in parsed]})
        return parent, rev, s, files, parsed, fingerprint

    @staticmethod
    def report_period(doc):
        from year_link import period
        try: return tuple(d.isoformat() for d in period(doc))
        except ValueError: return ('unrecognised',)

    def import_files(self, token, workbook, data, apply=False):
        parent, rev, state, files, parsed, fingerprint = self.prepare(token, workbook, data)
        preview = {'revision': rev, 'preview_digest': fingerprint, 'results': [
            {'key': p['key'], 'party': p['document']['party'], 'opening': p['document']['opening'],
             'closing': p['document']['closing'], 'reconciled': p['document']['reconciled'],
             'entries': len(p['document']['entries']), 'warnings': p['document']['warnings'],
             'mapping_plan': mapping_plan(p['document'], state),
             'existing_id': p['existing_id'], 'candidates': p['candidates'],
             'comparison': {name: sum(x['status'] == name for x in compare_import(self.ledger(state, p['candidates'][0])['document']['entries'], p['document']['entries'])) for name in ('New', 'Changed', 'Already imported')} if len(p['candidates']) == 1 else {},
             'status': 'Already imported' if p['existing_id'] else 'Review replacement' if p['candidates'] else 'New'} for p in parsed]}
        if not apply: return preview
        if data.get('preview_digest') != fingerprint:
            raise AuthError('Preview changed or expired. Preview the files again.', 409)
        replacements = data.get('replacements', {})
        if not isinstance(replacements, dict) or any(not isinstance(v, str) for v in replacements.values()) or set(replacements)-{p['key'] for p in parsed if p['candidates']}:
            raise AuthError('Invalid replacement selections', 400)
        if len(set(replacements.values())) != len(replacements):
            raise AuthError('An existing statement can be replaced only once per batch', 400)
        for p in parsed:
            if p['candidates'] and replacements.get(p['key']) not in p['candidates']:
                raise AuthError('Select the matching existing ledger before applying a changed statement', 409)
        if replacements: text(data.get('reason'), 'statement replacement reason')
        with self.accounts._tx() as db:
            u = self.store.user(db, token, 'import_statements'); require_permission(u, 'edit_ledger')
            _, current_rev, s = self.load(db, u['id'], workbook); self.expected(current_rev, rev)
            for f in files:
                if f.get('file_id'):
                    r = self.store.row(db, u['id'], f['file_id'], kind='files')
                    self.expected(r['revision'], f['file_revision'])
            saved_files = {}; imported = []
            for p in parsed:
                if p['existing_id']:
                    imported.append({'id': p['existing_id'], 'status': 'Already imported'}); continue
                fi = p['file_index']; f = files[fi]
                if fi not in saved_files:
                    fid = f.get('file_id') or uuid.uuid4().hex
                    if not f.get('file_id'):
                        db.execute('INSERT INTO workspace_documents VALUES(?,?,?,?,?,1,0,?)', (u['id'], fid, 'files', parent['project'], workbook, encode({k:f[k] for k in ('name','content_base64')})))
                    saved_files[fi] = fid
                doc = p['document']; prior = self.ledger(s, replacements[p['key']]) if p['candidates'] else None
                if prior: party_id = prior['party_id']
                else:
                    party_id = uuid.uuid4().hex
                    db.execute('INSERT INTO workspace_documents VALUES(?,?,?,?,?,1,0,?)', (u['id'], party_id, 'parties', parent['project'], workbook, encode({'name': doc['party'], 'state': doc.get('state', ''), 'hq': doc.get('hq', ''), 'reference': doc.get('location', '')})))
                lid = uuid.uuid4().hex
                ledger = {'id': lid, 'file_id': saved_files[fi], 'file_sha256': p['file_sha256'], 'source_index': p['source_index'],
                          'party_id': party_id, 'document': doc, 'reviews': {}, 'mappings': {}, 'superseded_by': None,
                          'replacement_reason': data.get('reason', '') if prior else ''}
                # Carry reviewed decisions only for exactly unchanged source rows.
                # Changed/new rows require fresh review and are never auto-merged.
                if prior:
                    old_by = {}
                    for i,e in enumerate(prior['document']['entries']): old_by.setdefault(digest(source_content(e)), []).append(i)
                    for i,e in enumerate(doc['entries']):
                        matches = old_by.get(digest(source_content(e)), [])
                        if len(matches) == 1:
                            oi = matches[0]
                            if str(oi) in prior['reviews']: ledger['reviews'][str(i)] = copy.deepcopy(prior['reviews'][str(oi)])
                            for j in range(len(e.get('items', []))):
                                if f'{oi}:{j}' in prior['mappings']: ledger['mappings'][f'{i}:{j}'] = prior['mappings'][f'{oi}:{j}']
                    prior['superseded_by'] = lid
                # Resolve identities only; printed source and financial settings stay intact.
                for key, decision in mapping_plan(doc, s).items():
                    if decision['product_id'] and key not in ledger['mappings']:
                        ledger['mappings'][key] = decision['product_id']
                s['ledgers'].append(ledger); imported.append({'id': lid, 'status': 'Imported'})
            if any(r['status'] == 'Imported' for r in imported):
                rev = self.save(db, u['id'], workbook, rev, s, 'ledger_batch_imported')
            return {'revision': rev, 'results': imported}

    def resolve_mappings(self, token, workbook, data):
        fields(data, {'revision', 'ledger_id'})
        with self.accounts._tx() as db:
            u = self.store.user(db, token, 'edit_ledger')
            _, rev, s = self.load(db, u['id'], workbook)
            self.expected(rev, data['revision'])
            r = self.ledger(s, data['ledger_id'])
            changed = 0
            for key, decision in mapping_plan(r['document'], s).items():
                if key not in r['mappings'] and decision['product_id']:
                    r['mappings'][key] = decision['product_id']; changed += 1
            if changed:
                rev = self.save(db, u['id'], workbook, rev, s, 'ledger_known_products_reused', r['id'])
            return {'revision': rev, 'mapped': changed}

    def mapping(self, token, workbook, data):
        fields(data, {'revision', 'ledger_id', 'entry_index', 'item_index'}, {'same_name', 'product_id', 'new_product'})
        if type(data.get('same_name', False)) is not bool:
            raise AuthError('Invalid mapping scope', 400)
        if ('product_id' in data) == ('new_product' in data):
            raise AuthError('Choose an existing product or enter a new product', 400)
        with self.accounts._tx() as db:
            u = self.store.user(db, token, 'edit_ledger')
            _, rev, s = self.load(db, u['id'], workbook); self.expected(rev, data['revision'])
            r = self.ledger(s, data['ledger_id'])
            e = index(data['entry_index'], r['document']['entries'])
            item = index(data['item_index'], e.get('items', []))
            if 'new_product' in data:
                require_permission(u, 'edit_schemes')
                values = data['new_product']
                fields(values, {'name', 'crop', 'packing_kg'}, {'segment'})
                values = {**values, 'name': text(values['name'], 'product name', 200),
                          'crop': ' '.join(text(values['crop'], 'crop', 200).split()),
                          'segment': ' '.join(text(values.get('segment') or 'Awaiting scheme', 'segment', 200).split())}
                choices = self.saved_choices(db, u['id'], workbook, s)
                values['crop'] = next((c for c in choices['crops'] if c.casefold() == values['crop'].casefold()), values['crop'])
                values['segment'] = next((c for c in choices['segments'].get(values['crop'], []) if c.casefold() == values['segment'].casefold()), values['segment'])
                product = {**values, 'id': uuid.uuid4().hex, 'aliases': []}
                validate_config([product], [])
                # Reuse a catalogue identity instead of creating a duplicate.
                matches = [p for p in s['catalogue'] if all(str(p[k]).strip().casefold() == str(product[k]).strip().casefold()
                           for k in ('name', 'crop')) and number(p['packing_kg']) == number(product['packing_kg'])]
                if len(matches) > 1:
                    raise AuthError('Several saved products share this name/crop/packing; choose the correct existing product', 409)
                if matches: product = matches[0]
                if product not in s['catalogue']:
                    validate_config([*s['catalogue'], product], s['periods'], s)
                    s['catalogue'].append(product)
            else:
                product = next((p for p in s['catalogue'] if p['id'] == data['product_id']), None)
            if not product:
                raise AuthError('Choose an existing workbook product; adding products requires Edit schemes', 400)
            if not packing_compatible(item, product):
                raise AuthError('Source packing differs from this product. Keep DAWAT/other packing groups separate.', 400)
            for i, entry in enumerate(r['document']['entries']):
                for j, other in enumerate(entry.get('items', [])):
                    if (i, j) == (data['entry_index'], data['item_index']) or data.get('same_name') and mapping_identity(other) == mapping_identity(item):
                        if not packing_compatible(other, product):
                            raise AuthError('A grouped source item has conflicting packing', 400)
                        r['mappings'][f'{i}:{j}'] = product['id']
            return {'revision': self.save(db, u['id'], workbook, rev, s, 'ledger_product_mapped', r['id']), 'product_id': product['id']}

    @staticmethod
    def is_journal(e):
        import re
        header = ((e.get('source_lines') or [{}])[0]).get('text', '')
        return str(e.get('voucher_family', '')).lower() == 'journal' or bool(re.search(r'\bJournal\b', header, re.I))

    @staticmethod
    def validate_review(r, state, ei, review):
        fields(review, {'reason'}, {'kind','season','cn_class','crop'})
        text(review['reason'], 'review reason')
        e=index(ei,r['document']['entries'])
        kind=review.get('kind', e['kind'])
        if not isinstance(kind, str) or kind not in {'sale','return','ipt_in','ipt_out','posted_cn','adjustment','unknown','receipt'}:
            raise AuthError('Invalid voucher classification',400)
        if (e['kind']=='receipt' or kind=='receipt') and kind!=e['kind']:
            raise AuthError('Receipt type and original dates cannot be changed',400)
        if kind=='return' and not e.get('items'): raise AuthError('Material return requires source item quantities',400)
        if kind in {'sale','return','ipt_in','ipt_out'} and not e.get('items'): raise AuthError('Stock classification requires source items',400)
        if 'season' in review:
            period=next((p for p in state['periods'] if p['name']==review['season']),None)
            if not period: raise AuthError('Choose a saved working period',400)
            if kind=='receipt': raise AuthError('Receipt eligibility always uses the original date',400)
            if kind in {'ipt_in','ipt_out'} and not period['start']<=e['date']<=period['end']:
                if not period['end']<e['date']<=period['cutoff']: raise AuthError('Late IPT must be after period end and within its cutoff',400)
        if review.get('cn_class') == 'scheme' and LedgerService.is_journal(e):
            raise AuthError('Journal CNs are excluded from scheme CN/NRV; classify as freight or other adjustment', 400)
        if 'cn_class' in review:
            if kind!='posted_cn' or not isinstance(review['cn_class'], str) or review['cn_class'] not in {'scheme','freight','other'}:
                raise AuthError('Choose scheme, freight or other for a posted CN',400)
        if 'crop' in review and (not isinstance(review['crop'], str) or review['crop'] not in {p['crop'] for p in state['catalogue']}):
            raise AuthError('Choose an existing crop',400)
        if isinstance(review.get('cn_class'), str) and review.get('cn_class') in {'freight','other'} and 'crop' in review:
            raise AuthError('Freight/other CN does not receive a crop mapping',400)

    def review(self, token, workbook, data):
        fields(data, {'revision','ledger_id','entry_index','review'})
        with self.accounts._tx() as db:
            u=self.store.user(db,token,'edit_ledger'); _,rev,s=self.load(db,u['id'],workbook); self.expected(rev,data['revision'])
            r=self.ledger(s,data['ledger_id']); self.validate_review(r,s,data['entry_index'],data['review'])
            r['reviews'][str(data['entry_index'])]=data['review']
            return {'revision':self.save(db,u['id'],workbook,rev,s,'ledger_voucher_reviewed',r['id'])}

    def reread(self,token,workbook,data):
        fields(data,{'revision','ledger_id'})
        with self.accounts._tx() as db:
            u=self.store.user(db,token,'import_statements'); _,rev,s=self.load(db,u['id'],workbook); self.expected(rev,data['revision'])
            r=self.ledger(s,data['ledger_id']); f=self.store.row(db,u['id'],r['file_id'],kind='files'); raw=base64.b64decode(json.loads(f['payload'])['content_base64'])
        docs=self.parse(raw,s); doc=index(r['source_index'],docs)
        return {'revision':rev,'comparison':[{'status':p['status'],'reference':p['incoming']['reference'],'date':p['incoming']['date']} for p in compare_import(r['document']['entries'],doc['entries'])],
                'warnings':doc['warnings'],'read_only':True}

    def summary(self,token,workbook,data):
        fields(data,{'ledger_id','season'})
        with self.accounts._tx() as db:
            u=self.store.user(db,token); _,rev,s=self.load(db,u['id'],workbook)
            r=self.ledger(s,data['ledger_id']); period=next((p for p in s['periods'] if p['name']==data['season']),None)
            if not period: raise AuthError('Choose a saved working period',400)
            return {'revision':rev,**self.build_summary(r,s,period)}

    @staticmethod
    def build_summary(r,s,period):
        rows={}; receipts=[]; posted=[]; unresolved=[]
        doc=LedgerService.effective(r,s)
        for i,e in enumerate(doc['entries']):
            review=e['web_review']; kind=e['kind']; dt=e['date']
            assigned=review.get('season'); in_dates=period['start']<=dt<=period['end']
            included=assigned==period['name'] if assigned else in_dates
            if kind=='receipt':
                receipts.append({'entry_index':i,'date':dt,'original_date':(e.get('original') or e)['date'],'amount':e['credit'],'in_working_period':in_dates})
                continue
            if kind=='posted_cn':
                posted.append({'entry_index':i,'date':dt,'amount':e['credit'],'season':assigned,
                               'cn_class':review.get('cn_class','unclassified'),'crop':review.get('crop'),
                               'included_in_selected_season':included and review.get('cn_class')=='scheme' and bool(assigned) and not LedgerService.is_journal(e)})
                # A journal CN is never a material sales return and is never
                # silently treated as a current-season benefit deduction.
                if included and (not review.get('cn_class') or review.get('cn_class')=='scheme' and not assigned):
                    unresolved.append({'entry_index':i,'message':'Review posted CN type and benefit season; posting date alone is insufficient'})
                continue
            if not included: continue
            if e.get('classification_required'):
                unresolved.append({'entry_index':i,'message':'Voucher classification needs review'})
            if not isinstance(kind, str) or kind not in {'sale','return','ipt_in','ipt_out'}: continue
            for j,item in enumerate(e.get('items',[])):
                product=next((p for p in s['catalogue'] if p['id']==item.get('product')),None)
                key=(item.get('product') or item['name'],item['unit'])
                row=rows.setdefault(key,{'product_id':item.get('product'),'product':product['name'] if product else item['name'],
                                       'crop':product['crop'] if product else 'Unmapped','segment':product['segment'] if product else '',
                                       'packing_kg':product['packing_kg'] if product else None,'unit':item['unit'],
                                       'supply':Decimal(0),'returns':Decimal(0),'ipt_in':Decimal(0),'ipt_out':Decimal(0)})
                qty = number(item['qty'])
                if qty < 0 or item['unit'] == 'packet' and qty != qty.to_integral_value():
                    unresolved.append({'entry_index':i,'item_index':j,'message':'Invalid quantity: packet quantities must be whole and stock quantity nonnegative'})
                row[{'sale':'supply','return':'returns','ipt_in':'ipt_in','ipt_out':'ipt_out'}[kind]]+=number(item['qty'])
                if not product: unresolved.append({'entry_index':i,'item_index':j,'message':'Confirm product and packing mapping'})
        for row in rows.values():
            row['net_supply']=row['supply']+row['ipt_in']-row['ipt_out']
            row['net_sold']=row['net_supply']-row['returns']
            row['net_sold_kg']=row['net_sold'] if row['unit']=='kg' else row['net_sold']*number(row['packing_kg']) if row['packing_kg'] else None
            if row['net_sold']<0: unresolved.append({'message':'Returns exceed complete-period supply including reviewed IPT','product':row['product']})
        return {'season':period,'opening':doc['opening'],'closing':doc['closing'],'reconciled':doc['reconciled'],
                'products':list(rows.values()),'receipts':receipts,'posted_CNs':posted,'needs_review':unresolved,
                'note':'Ledger balances retain all posted transactions. This is season stock review, not a CN calculation.'}

    def audit_result(self,s,data):
        fields(data,{'start','end'}, {'ledger_ids'})
        start,end=day(data['start']),day(data['end'])
        if start>end: raise AuthError('Checking period is reversed',400)
        ids=data.get('ledger_ids')
        if ids is not None:
            if not isinstance(ids,list) or not ids or any(not isinstance(v,str) for v in ids) or len(set(ids))!=len(ids): raise AuthError('Choose ledger IDs',400)
            ledgers=[self.ledger(s,lid) for lid in ids]
        else: ledgers=[r for r in s['ledgers'] if not r['superseded_by']]
        docs=[self.effective(r,s) for r in ledgers]
        cfg=self.settings(s); cfg['audit_finding_reviews']=s['audit_reviews']
        # Catalogue mapping influences read-only reporting without editing schemes.
        by_product={p['id']:p for p in cfg['products']}
        classifications={}; crop_mappings={}; conflicts=set()
        for doc in docs:
            for e in doc['entries']:
                for item in e.get('items',[]):
                    if item.get('product') in by_product:
                        aliases=by_product[item['product']]['aliases']
                        if item['name'] not in aliases: aliases.append(item['name'])
                r=e['web_review']; n=narration(e)
                if r.get('cn_class'):
                    if n in classifications and classifications[n]!=r['cn_class']: conflicts.add(n)
                    classifications[n]=r['cn_class']
                if r.get('crop'): crop_mappings[n]=r['crop']
        cfg['audit_cn_classifications']={k:v for k,v in classifications.items() if k not in conflicts}
        cfg['audit_crop_mappings']={k:v for k,v in crop_mappings.items() if k not in conflicts}
        return audit_documents(docs,start,end,cfg)

    def audit(self,token,workbook,data):
        with self.accounts._tx() as db:
            u=self.store.user(db,token); _,rev,s=self.load(db,u['id'],workbook)
            return {'revision':rev,**self.audit_result(s,data)}

    def audit_review(self,token,workbook,data):
        fields(data,{'revision','start','end','review_id','reason'}, {'reset','ledger_ids'})
        text(data['review_id'],'finding identity',100)
        if type(data.get('reset',False)) is not bool: raise AuthError('Invalid reset',400)
        if not data.get('reset'): text(data['reason'],'not-applicable reason')
        with self.accounts._tx() as db:
            u=self.store.user(db,token,'edit_ledger'); _,rev,s=self.load(db,u['id'],workbook); self.expected(rev,data['revision'])
            result=self.audit_result(s,{k:data[k] for k in ('start','end','ledger_ids') if k in data})
            finding=next((f for f in result['findings'] if f['review_id']==data['review_id']),None)
            if not finding: raise AuthError('Finding evidence changed. Run the audit again.',409)
            if data.get('reset'): s['audit_reviews'].pop(data['review_id'],None)
            else: s['audit_reviews'][data['review_id']]={'status':'not_applicable','reason':data['reason'],'start':data['start'],'end':data['end'],'type':finding['type']}
            return {'revision':self.save(db,u['id'],workbook,rev,s,'ledger_audit_reviewed')}

    @staticmethod
    def link_stale(s,link):
        try:
            a=LedgerService.ledger(s,link['previous_id']); b=LedgerService.ledger(s,link['current_id'])
            return signature(a['document'])!=link['previous_signature'] or signature(b['document'])!=link['current_signature']
        except AuthError: return True

    def year_link(self,token,workbook,data,apply=False):
        fields(data,{'revision','previous_id','current_id'}, {'identity_reason','confirmed','reason'})
        reason=data.get('identity_reason',''); text(reason,'identity reason',500,True)
        with self.accounts._tx() as db:
            u=self.store.user(db,token,'edit_ledger' if apply else 'view_workspace')
            _,rev,s=self.load(db,u['id'],workbook); self.expected(rev,data['revision'])
            previous=self.ledger(s,data['previous_id']); current=self.ledger(s,data['current_id'])
            if previous['id']==current['id']: raise AuthError('Select two financial-year ledgers',400)
            try:
                result=analyse_pair(previous['document'],current['document'],reason)
                if not apply: return {'revision':rev,'review':result}
                confirmed=data.get('confirmed',{})
                if not isinstance(confirmed,dict): raise AuthError('Choose original receipts and remaining amounts',400)
                for v in confirmed.values(): number(v)
                text(data.get('reason'),'Year Link review note')
                # Reuse the preserved opening-credit cap and original-date source builder.
                record=attach_link({**current['document'],'status':'draft','allocations':[],'opening_sources':[]},previous['document'],current['document'],confirmed,data['reason'],reason)
            except (ValueError,ArithmeticError) as exc: raise AuthError(str(exc),400) from None
            s['year_links'][current['id']]={'previous_id':previous['id'],'current_id':current['id'],
                'previous_signature':result['previous_signature'],'current_signature':result['current_signature'],'record':record}
            return {'revision':self.save(db,u['id'],workbook,rev,s,'ledger_year_linked',current['id']),
                    'opening_sources':record['opening_sources']}

    def protect(self,db,owner,row,method='DELETE',data=None):
        if method == 'PATCH' and row['kind'] in {'parties','workbooks'}:
            return  # Editable display metadata never replaces immutable PDF evidence.
        if method == 'PATCH' and row['kind'] == 'files':
            previous = json.loads(row['payload'])
            if data['data'].get('content_base64') == previous.get('content_base64'):
                return  # Renaming retains exactly the saved source bytes.
        for state_row in db.execute('SELECT workbook,payload FROM ledger_workspaces WHERE owner=?',(owner,)):
            s=json.loads(state_row['payload'])
            billing_sources=s.get('billing_audit',{}).get('sources',[])
            if (row['id']==state_row['workbook'] and billing_sources) or any(ref.get('web_file_id')==row['id'] for ref in billing_sources):
                raise AuthError('Saved billing-audit source evidence is protected',409)
            if row['id']==state_row['workbook'] and s['ledgers']:
                raise AuthError('Workbook has saved ledger history; it cannot be archived here',409)
            if any(row['id'] in (r['file_id'],r['party_id']) for r in s['ledgers']):
                raise AuthError('Linked source file/party is protected by saved ledger history',409)

    def export_bundle(self,db,owner,project):
        ids={r['id'] for r in db.execute('SELECT id FROM workspace_documents WHERE owner=? AND project=? AND deleted=0 AND kind=?',(owner,project,'workbooks'))}
        return [{'workbook':r['workbook'],'state':json.loads(r['payload'])} for r in db.execute('SELECT workbook,payload FROM ledger_workspaces WHERE owner=?',(owner,)) if r['workbook'] in ids]

    def validate_bundle(self,bundle,documents):
        if not isinstance(bundle,list) or len(bundle)>1000: raise AuthError('Invalid ledger backup',400)
        seen=set(); out=[]; all_lids=set()
        for part in bundle:
            fields(part,{'workbook','state'})
            w=documents.get(part['workbook']) if isinstance(part['workbook'],str) else None
            if not w or w['kind']!='workbooks' or part['workbook'] in seen: raise AuthError('Invalid ledger workbook reference',400)
            seen.add(part['workbook']); s=copy.deepcopy(part['state'])
            fields(s,set(empty_state()),{'billing_audit'})
            if 'billing_audit' in s:
                from .billing_audit import validate as validate_billing
                validate_billing(s['billing_audit'],s['catalogue'])
            validate_config(s['catalogue'],s['periods'])
            if not isinstance(s['ledgers'],list) or len(s['ledgers'])>10000 or not isinstance(s['year_links'],dict) or not isinstance(s['audit_reviews'],dict): raise AuthError('Invalid ledger backup state',400)
            lids=set(); parsed={}
            for r in s['ledgers']:
                fields(r,{'id','file_id','file_sha256','source_index','party_id','document','reviews','mappings','superseded_by','replacement_reason'})
                identifier(r['id']); text(r['replacement_reason'],'replacement reason',500,True)
                if r['id'] in lids or r['id'] in all_lids or r['id'] in documents: raise AuthError('Duplicate ledger identity',400)
                lids.add(r['id']); all_lids.add(r['id'])
                f=documents.get(r['file_id']) if isinstance(r['file_id'],str) else None
                p=documents.get(r['party_id']) if isinstance(r['party_id'],str) else None
                if not f or f['kind']!='files' or f['workbook'] not in (None,part['workbook']) or not p or p['kind']!='parties' or p['workbook']!=part['workbook']: raise AuthError('Invalid source/party relationship',400)
                raw=base64.b64decode(f['data']['content_base64'],validate=True)
                if hashlib.sha256(raw).hexdigest()!=r['file_sha256']: raise AuthError('Source file fingerprint changed',400)
                if r['file_id'] not in parsed: parsed[r['file_id']]=self.parse(raw,s)
                original=index(r['source_index'],parsed[r['file_id']])
                # Do not trust backup-supplied source originals, balances or dates.
                if signature(original)!=signature(r['document']): raise AuthError('Ledger source differs from saved PDF; import the PDF for review',400)
                r['document']=original
                if not isinstance(r['reviews'],dict) or not isinstance(r['mappings'],dict): raise AuthError('Invalid ledger reviews',400)
                for k,review in r['reviews'].items():
                    if not k.isdigit() or str(int(k))!=k: raise AuthError('Invalid review index',400)
                    self.validate_review(r,s,int(k),review)
                for key,pid in r['mappings'].items():
                    if not isinstance(key,str) or not isinstance(pid,str) or not any(p['id']==pid for p in s['catalogue']): raise AuthError('Invalid product mapping',400)
                    bits=key.split(':')
                    if len(bits)!=2 or any(not b.isdigit() or str(int(b))!=b for b in bits): raise AuthError('Invalid product mapping index',400)
                    item = index(int(bits[1]),index(int(bits[0]),r['document']['entries']).get('items',[]))
                    detected = (item.get('mapping_suggestion') or {}).get('detected_packing_kg')
                    product = next(p for p in s['catalogue'] if p['id'] == pid)
                    if detected and number(detected) != number(product['packing_kg']):
                        raise AuthError('Backup mapping changes source packing identity', 400)
            for r in s['ledgers']:
                if r['superseded_by'] == r['id']:
                    raise AuthError('Invalid self-replacement history', 400)
                if r['superseded_by'] is not None and r['superseded_by'] not in lids: raise AuthError('Invalid ledger history relationship',400)
            # Rebuild Year Link proof from validated PDFs and explicit original
            # remaining amounts, never import client-created opening sources.
            rebuilt={}
            for key,v in s['year_links'].items():
                fields(v,{'previous_id','current_id','previous_signature','current_signature','record'})
                prev=self.ledger(s,v['previous_id'],False); cur=self.ledger(s,v['current_id'],False)
                if key!=cur['id']: raise AuthError('Invalid Year Link identity',400)
                link=v['record'].get('prior_year_link',{})
                try:
                    result=analyse_pair(prev['document'],cur['document'],link.get('identity_reason',''))
                    record=attach_link({**cur['document'],'status':'draft','allocations':[],'opening_sources':[]},prev['document'],cur['document'],link['confirmed_remaining'],link['review_note'],link.get('identity_reason',''))
                except (ValueError,KeyError,ArithmeticError): raise AuthError('Invalid Year Link backup',400) from None
                rebuilt[key]={'previous_id':prev['id'],'current_id':cur['id'],'previous_signature':result['previous_signature'],'current_signature':result['current_signature'],'record':record}
            s['year_links']=rebuilt
            # Only structurally valid historical NA notes; evidence keys decide
            # whether they apply to current server-generated findings.
            for key,v in s['audit_reviews'].items():
                if not isinstance(key,str) or len(key)!=64: raise AuthError('Invalid audit evidence key',400)
                fields(v,{'status','reason','start','end','type'})
                if v['status']!='not_applicable': raise AuthError('Invalid audit status',400)
                text(v['reason']); text(v['type']); day(v['start']); day(v['end'])
            if 'billing_audit' in s:
                from .billing_audit import run as run_billing
                billing_docs=[]
                for ref in s['billing_audit']['sources']:
                    if 'web_ledger_id' in ref:
                        source=self.ledger(s,ref['web_ledger_id'],False)
                        billing_docs.append(self.effective(source,s))
                    else:
                        f=documents.get(ref['web_file_id'])
                        if not f or f['kind']!='files' or f['workbook']!=part['workbook']:raise AuthError('Invalid billing source ownership',400)
                        docs=self.parse(base64.b64decode(f['data']['content_base64'],validate=True),s)
                        i=ref['web_document_index']
                        if i>=len(docs):raise AuthError('Invalid billing source document',400)
                        billing_docs.append(docs[i])
                # Selections are user-reviewed, never imported as a precomputed result.
                run_billing(billing_docs,s,'0001-01-01','9999-12-31',strict=True)
            out.append({'workbook':part['workbook'],'state':s})
        return out

    def import_bundle(self,db,user,mapping,bundle):
        if not bundle:return
        require_permission(user,'edit_schemes'); require_permission(user,'edit_ledger'); require_permission(user,'import_statements')
        for part in bundle:
            s=copy.deepcopy(part['state']); lidmap={r['id']:mapping[r['id']] for r in s['ledgers']}
            for r in s['ledgers']:
                r['id']=lidmap[r['id']]; r['file_id']=mapping[r['file_id']]; r['party_id']=mapping[r['party_id']]
                r['superseded_by']=lidmap.get(r['superseded_by'])
            if 'billing_audit' in s:
                for ref in s['billing_audit']['sources']:
                    field='web_ledger_id' if 'web_ledger_id' in ref else 'web_file_id'
                    ref[field]=mapping[ref[field]]
            s['year_links']={lidmap[k]:{**v,'previous_id':lidmap[v['previous_id']],'current_id':lidmap[v['current_id']]} for k,v in s['year_links'].items()}
            db.execute('INSERT INTO ledger_workspaces VALUES(?,?,1,?)',(user['id'],mapping[part['workbook']],encode(s)))
