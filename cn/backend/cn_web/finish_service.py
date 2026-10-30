"""Owned Phase 6 orchestration around the preserved Store/reporting functions."""
import copy
import json
from contextlib import contextmanager

from .ledger_service import digest, fields, text
from .security import AuthError, require_permission
from store import Store, dump
from engine import compute, late_ipt_issue_conflict
from year_link import traced_credit_conflict
from reporting import report, product_rows, csv_text
from territory import territory_report
from workbook_print import workbook_print
from importer import source_content


def frozen_result(record):
    """Reproducible calculation proof, including the web stock display mask."""
    result = compute(record, record.get('web_calculation_settings') or record['frozen_settings'])
    if record.get('web_source'):
        for e in record['entries']:
            if e.get('items') and all(i.get('_web_season_excluded') and i.get('exclude') for i in e['items']):
                result.get('stock_scope', {})[e['id']] = False
    return json.loads(dump(result))


def selected_stock(record):
    result = record.get('result', {})
    cfg = record.get('frozen_settings', {})
    season = next((s for s in cfg.get('seasons', []) if s['name'] == record.get('season')), {})
    selected = set()
    for entry in record.get('entries', []):
        if entry.get('kind') not in ('sale', 'return', 'ipt_in', 'ipt_out'):
            continue
        include = result.get('stock_scope', {}).get(entry['id'])
        if include is None:
            include = season.get('start', '') <= entry.get('date', '') <= season.get('end', '')
        if not include:
            continue
        for item in entry.get('items', []):
            if item.get('exclude'):
                continue
            physical=source_content({'date':(entry.get('original') or entry).get('date'),
                'reference':entry.get('reference'),'kind':entry.get('kind'),'items':[item]})
            selected.add(digest(physical))
    return selected


class Books:
    """Read-only project view expected by the unchanged reporting functions."""
    def __init__(self, stores, metadata):
        self.stores, self.meta = stores, metadata
    def metadata(self, key):
        return self.meta[key]
    def list(self):
        return [v for k, v in self.meta.items() if k != 'legacy']
    def get(self, key):
        return self.stores[key]


class FinishService:
    def __init__(self, calculator):
        self.calculator = calculator

    @contextmanager
    def books(self, db, user, project):
        from .calculator_service import Runtime
        stores = {}; metadata = {'legacy': {'id': 'legacy', 'name': 'Unassigned', 'state': ''}}
        try:
            stores['legacy'] = Runtime(None, {'catalogue': [], 'periods': []}, self.calculator)
            rows = db.execute("SELECT * FROM workspace_documents WHERE owner=? AND project=? AND kind='workbooks' AND deleted=0", (user['id'], project)).fetchall()
            for row in rows:
                key = row['id']; metadata[key] = {'id': key, **json.loads(row['payload'])}
                _, _, source = self.calculator.ledger.load(db, user['id'], key)
                payload = db.execute('SELECT payload FROM calculator_workspaces WHERE owner=? AND workbook=?', (user['id'], key)).fetchone()
                stores[key] = Runtime(json.loads(payload['payload']) if payload else None, source, self.calculator)
            yield Books(stores, metadata)
        finally:
            for store in stores.values(): store.connection.close()

    def all_records(self, db, owner):
        # Include archived workbooks/projects for duplicate-issue protection.
        return [(row['workbook'], json.loads(raw[2]))
                for row in db.execute('SELECT workbook,payload FROM calculator_workspaces WHERE owner=?', (owner,))
                for raw in json.loads(row['payload'])['records']]

    @staticmethod
    def expected(body):
        text(body['id'], 'calculation ID', 200)
        if 'revision' in body and (type(body['revision']) is not int or body['revision']<1):
            raise AuthError('Choose the current saved calculation revision', 400)

    def finalise(self, st, body):
        fields(body, {'id', 'revision'}); self.expected(body)
        st.finance = True
        raw = Store.get(st, body['id']); st.source_finance = bool(raw.get('web_source'))
        projected = st.project(raw)  # revalidates current source/period/Year Link
        st.check_payment_usage(projected)
        original_settings = Store.settings(st)
        calculation_settings = st.settings()
        # Store.finalise reads SQLite directly. Supply the same private settings
        # envelope used by the Phase 5 calculator, never change the saved config.
        with st.db() as c:
            c.execute('UPDATE records SET data=? WHERE id=?', (dump(projected), raw['id']))
            c.execute('UPDATE settings SET data=? WHERE version=?', (dump(calculation_settings), original_settings['version']))
        frozen = Store.finalise(st, raw['id'], body['revision'])
        with st.db() as c:
            c.execute('UPDATE settings SET data=? WHERE version=?', (dump(original_settings), original_settings['version']))
        if raw.get('web_source'):
            frozen['web_calculation_settings'] = calculation_settings
            frozen['frozen_settings'] = original_settings
            frozen['result'] = frozen_result(frozen)
            if frozen['result']['issues']:
                raise AuthError('Resolve all calculation issues before finalising', 409)
        with st.db() as c:
            c.execute('UPDATE records SET data=? WHERE id=?', (dump(frozen), raw['id']))
        return frozen

    def issue(self, db, user, workbook, st, body):
        fields(body, {'id', 'revision'}); self.expected(body)
        record = Store.get(st, body['id'])
        if record.get('status') != 'finalised':
            raise AuthError('Only a finalised calculation can be issued', 409)
        # A frozen result remains viewable; changed source must be reviewed before
        # posting a formerly finalised draft as issued.
        if record.get('web_source'):
            check = copy.deepcopy(record); check['status'] = 'draft'; st.project(check)
        all_rows = self.all_records(db, user['id'])
        from prior_payments import conflicts
        conflicts(record,[r for _,r in all_rows])
        cfg = record['frozen_settings']
        season = next(s for s in cfg['seasons'] if s['name'] == record['season'])
        proposed = {cn['key'] for cn in record['result']['proposals']}
        for other_book, old in all_rows:
            if old.get('status') != 'issued' or not Store.same_party(record, old): continue
            same_lineage = workbook == other_book and (record.get('lineage') or record['id']) == (old.get('lineage') or old['id']) and record['season'] == old['season']
            if same_lineage: continue
            previous = next((s for s in old['frozen_settings']['seasons'] if s['name'] == old['season']), {})
            if late_ipt_issue_conflict(record, old) or selected_stock(record) & selected_stock(old):
                raise AuthError('Source stock/IPT already belongs to another issued calculation; revise the original calculation.', 409)
            if previous.get('start') and season.get('start') and season['start'] <= previous['end'] and previous['start'] <= season['end'] and proposed.intersection(cn['key'] for cn in old['result']['proposals']):
                raise AuthError('Party/benefit overlaps an issued calculation; revise the original calculation.', 409)
        if traced_credit_conflict(record, [r for _, r in all_rows]):
            raise AuthError('Opening receipt credit is already used beyond its confirmed remaining amount', 409)
        return Store.issue(st, body['id'], body['revision'])

    def revise(self, st, body):
        fields(body, {'id'}, {'revision'}); self.expected(body)
        previous = Store.get(st, body['id'])
        if 'revision' in body and body['revision'] != previous['revision']:
            raise AuthError('Calculation changed; reopen it before revising', 409)
        record = Store.revise(st, body['id'])
        record.pop('web_calculation_settings', None)
        binding = record.get('web_source')
        if binding:
            source = st.service.ledger.ledger(st.ledger, binding['ledger_id'], False)
            original_source = source
            source = st.service.ledger.current_source(st.ledger, source['id'])
            doc = st.service.ledger.effective(source, st.ledger)
            link = st.ledger['year_links'].get(source['id'])
            if link and st.service.ledger.link_stale(st.ledger, link):
                raise AuthError('Review Year Link before revising this calculation', 409)
            changed = binding['revision'] != digest(source) or binding.get('year_link') != digest(link) or binding.get('periods') != digest(st.ledger['periods'])
            if changed:
                old_source={e['id']:e for e in original_source['document']['entries']}
                old_record={e['id']:e for e in record['entries']}
                fresh=[]
                for entry in doc['entries']:
                    prior=old_record.get(entry['id']); raw=old_source.get(entry['id'])
                    if prior and raw and digest(source_content(raw))==digest(source_content(entry)):
                        retained=copy.deepcopy(prior)
                        if prior.get('web_review')!=entry.get('web_review'):retained['kind']=entry['kind']
                        retained['web_review']=entry.get('web_review',{})
                        for old_item,new_item in zip(retained.get('items',[]),entry.get('items',[])):
                            for key in ('product','packing_kg','crop','segment','mapping_confirmed'):
                                if key in new_item:old_item[key]=new_item[key]
                        fresh.append(retained)
                    else:fresh.append(entry)
                fresh += [copy.deepcopy(e) for e in record['entries'] if e['id'] not in old_source]
            else:fresh=record['entries']
            record.update(entries=fresh, source=doc['source'], opening=doc['opening'] if doc['opening']!=original_source['document']['opening'] else record['opening'], closing=doc['closing'] if doc['closing']!=original_source['document']['closing'] else record['closing'],
                          web_source={'ledger_id': source['id'], 'revision': digest(source), 'year_link': digest(link), 'periods': digest(st.ledger['periods'])},
                          opening_sources=copy.deepcopy(link['record']['opening_sources']) if link else [])
            if link: record['prior_year_link'] = copy.deepcopy(link['record']['prior_year_link'])
            else: record.pop('prior_year_link', None)
            for entry in record['entries']:
                if entry.get('web_review'): entry['correction_reason'] = entry['web_review']['reason']
            st.finance = True; st.source_finance = True
            record = st.project(record)
            with st.db() as c:
                c.execute('UPDATE records SET data=? WHERE id=?', (dump(record), record['id']))
        return record

    def execute(self, db, user, project, workbook, meta, st, action, body):
        if action == 'finalise':
            require_permission(user, 'finalise'); return self.finalise(st, body)
        if action == 'issue':
            require_permission(user, 'issue_cn'); return self.issue(db, user, workbook, st, body)
        if action == 'revise':
            require_permission(user, 'edit_ledger'); require_permission(user, 'finalise')
            return self.revise(st, body)
        if action!='workbook-review':require_permission(user, 'export_print')
        if action in ('report', 'territory-report'):
            fields(body, set(), {'filters', 'csv'})
            filters = body.get('filters', {})
            if not isinstance(filters, dict) or set(filters) - {'workbook','state','season','crop','segment','product','party','hq'} or any(not isinstance(v, str) for v in filters.values()):
                raise AuthError('Invalid report filters', 400)
            with self.books(db, user, project) as books:
                result = territory_report(books, filters) if action == 'territory-report' else report(books, filters)
            return {'csv': csv_text(result['rows']), 'rows': len(result['rows']), 'notes': result['notes']} if action == 'report' and body.get('csv') else result
        if action in ('workbook-print','workbook-review'):
            fields(body, set(), {'record_ids','expected'})
            result = workbook_print(st, meta, body)
            for item in result.get('items', []):
                record = item['record']
                if record['status'] == 'draft':
                    try:
                        st.finance = True; st.source_finance = bool(record.get('web_source'))
                        item['result'] = st.calculate(record); item.pop('error', None)
                    except (ValueError, AuthError) as e:
                        item['error'] = str(e); item.pop('result', None)
            return result
        if action in ('product-csv', 'print-record'):
            if action == 'product-csv':
                fields(body, {'record'}); supplied = body['record']
                if not isinstance(supplied, dict) or not supplied.get('id'): raise AuthError('Save the calculation first', 400)
                record = Store.get(st, supplied['id'])
                if supplied.get('revision') != record['revision']: raise AuthError('Calculation changed; reopen it', 409)
            else:
                fields(body, {'id', 'revision'}); self.expected(body); record = Store.get(st, body['id'])
                if body['revision'] != record['revision']: raise AuthError('Calculation changed; reopen it', 409)
            st.finance = True; st.source_finance = bool(record.get('web_source'))
            result = st.calculate(record)
            if action == 'print-record': return {'record': record, 'result': result}
            cfg = record.get('frozen_settings') or st.settings()
            rows = product_rows(record, result, cfg, meta)
            return {'csv': csv_text(rows), 'rows': len(rows)}
        raise AuthError('Unknown report operation', 404)
