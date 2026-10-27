"""Reviewed clearing of saved draft allocations, preserving all ledger evidence."""
import copy,hashlib
from engine import D,compute
from store import dump


def clear_allocations(store,payload,apply=False):
    r=store.get(payload['id'])
    if r.get('deleted_at') or r.get('status')!='draft':
        raise ValueError('Restore the party or create a draft revision before clearing allocations')
    if payload.get('revision')!=r['revision']:
        raise ValueError('Calculation changed; reopen the clear preview')
    cfg=store.settings();scope=payload.get('scope');target=payload.get('target','')
    rows=r.get('allocations',[]);splits=r.get('cash_splits',[])
    if scope=='all':selected=list(rows)
    elif scope=='source':selected=[a for a in rows if a.get('source')==target]
    elif scope=='row':selected=[a for a in rows if a.get('id')==target]
    else:raise ValueError('Choose one allocation, one payment or all party allocations')
    if not selected and not (scope=='all' and splits):raise ValueError('No allocations remain for this selection')
    # Cash quantity belongs to a scheme/product, not a single receipt. Remove its
    # complete funding group so no orphan split or partial funding survives.
    cash_keys={(a.get('scheme'),a.get('product')) for a in selected if a.get('type')=='Cash'}
    removed_splits=[s for s in splits if scope=='all' or (s.get('scheme'),s.get('product')) in cash_keys]
    selected_ids={a['id'] for a in selected}
    removed=[a for a in rows if a['id'] in selected_ids or
             (a.get('type')=='Cash' and (a.get('scheme'),a.get('product')) in cash_keys)]
    removed_ids={a['id'] for a in removed}
    expected=hashlib.sha256(dump({'record':r,'settings':cfg,'scope':scope,'target':target}).encode()).hexdigest()
    if apply and payload.get('expected')!=expected:
        raise ValueError('Calculation or settings changed; reopen the clear preview')
    candidate=copy.deepcopy(r)
    candidate['allocations']=[a for a in candidate.get('allocations',[]) if a['id'] not in removed_ids]
    candidate['cash_splits']=[s for s in candidate.get('cash_splits',[]) if s not in removed_splits]
    before=compute(r,cfg);after=compute(candidate,cfg)
    released={}
    for a in removed:released[a.get('source','')]=released.get(a.get('source',''),D(0))+D(a.get('amount') or 0)
    plan={'expected':expected,'scope':scope,'target':target,'removed':removed,
          'cash_splits':removed_splits,'extra_rows':len(removed)-len(selected),
          'released_by_source':released,'released_total':sum(released.values(),D(0)),
          'previous_CN':before['new_CN_total'],'new_CN':after['new_CN_total'],
          'issues':after['issues']}
    if apply:return store.save(candidate)
    return plan
