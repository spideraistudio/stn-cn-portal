"""Read-only workbook print snapshots; one chosen version per party and season."""
import copy,hashlib,json
from decimal import Decimal
from store import dump
from engine import compute

def identity(r):
    return (str(r.get('party') or '').strip().casefold() or r['id'],str(r.get('location') or '').strip().casefold(),str(r.get('season') or ''))

def workbook_print(store,metadata,payload):
    # One SQLite read transaction fixes both records and settings for the report.
    with store.db() as c:
        c.execute('BEGIN')
        records=[json.loads(x[0]) for x in c.execute('SELECT data FROM records ORDER BY rowid')]
        settings=json.loads(c.execute('SELECT data FROM settings ORDER BY version DESC LIMIT 1').fetchone()[0])
    records=[r for r in records if not r.get('deleted_at')]
    digest=hashlib.sha256(dump({'records':records,'settings':settings,'metadata':metadata}).encode()).hexdigest()
    grouped={}
    for r in records:grouped.setdefault(identity(r),[]).append(r)
    groups=[]
    for key,versions in sorted(grouped.items()):
        versions.sort(key=lambda r:(bool(r.get('entries') or r.get('source')),r.get('saved_at',''),r.get('revision',0),r['id']),reverse=True)
        groups.append({'party':versions[0].get('party') or 'Unnamed calculation','location':versions[0].get('location',''),'season':versions[0].get('season',''),
                       'selected_id':versions[0]['id'],'versions':[{'id':r['id'],'status':r.get('status','draft'),'saved_at':r.get('saved_at',''),'revision':r.get('revision',0),'has_ledger':bool(r.get('entries') or r.get('source'))} for r in versions]})
    if 'record_ids' not in payload:return {'workbook':metadata,'expected':digest,'groups':groups}
    if payload.get('expected')!=digest:raise ValueError('Workbook changed; reopen the print selection and review again.')
    ids=payload['record_ids']
    if not isinstance(ids,list) or not ids or any(not isinstance(x,str) for x in ids) or len(ids)!=len(set(ids)):raise ValueError('Choose at least one calculation; duplicate selections are not allowed.')
    byid={r['id']:r for r in records}
    if any(i not in byid for i in ids):raise ValueError('A selected calculation is unavailable in this workbook.')
    selected=[byid[i] for i in ids]
    if len({identity(r) for r in selected})!=len(selected):raise ValueError('Choose one version per party and season to avoid duplicate CN totals.')
    selected.sort(key=lambda r:identity(r));items=[]
    for r in selected:
        try:
            if r.get('status') in ('finalised','issued'):
                if r.get('result') is None:raise ValueError('Saved frozen result unavailable; cannot reconstruct historical CNs.')
                result=copy.deepcopy(r['result'])
            else:
                draft=copy.deepcopy(r);draft.pop('frozen_settings',None);draft.pop('result',None);result=compute(draft,settings)
            items.append({'record':copy.deepcopy(r),'result':result})
        except (ValueError,ArithmeticError,KeyError) as exc:items.append({'record':copy.deepcopy(r),'error':str(exc)})
    return {'workbook':metadata,'settings':settings,'items':items,'expected':digest}
