"""Canonical, dated receipt reservations. No vouchers or ledger balances are rewritten."""
import copy
from datetime import date
from decimal import Decimal
from year_link import analyse_pair, signature

def amount(v):
    n=Decimal(str(v or '0'))
    if not n.is_finite() or n<0 or n>Decimal('1000000000000000'):raise ValueError('Invalid non-negative amount')
    return n

def exact(v):
    # PDF line breaks are extraction artefacts; words, punctuation and case remain significant.
    return ' '.join(str(v or '').split())

def party_match(a,b):
    keys=('party','address','location')
    left={k:exact(a.get(k)) for k in keys};right={k:exact(b.get(k)) for k in keys}
    ok=bool(left['party'] and left['address'] and left==right)
    issuer_a=exact(a.get('source',{}).get('issuer'));issuer_b=exact(b.get('source',{}).get('issuer'))
    ok=ok and issuer_a==issuer_b
    return {'matched':ok,'previous':left,'current':right,'message':'Exact seller name, address and location match' if ok else 'Seller name/address/location or issuing company differs or is missing. Linking blocked; no manual identity override.'}

def analyse(previous,current,start,end,approvals=None):
    match=party_match(previous,current)
    if not match['matched']:raise ValueError(match['message'])
    pair=analyse_pair(previous,current)
    start=date.fromisoformat(start).isoformat();end=date.fromisoformat(end).isoformat()
    if not pair['previous_start']<=start<=end<=pair['previous_end']:raise ValueError('Choose a receipt period within the previous financial year')
    entries=previous['entries'];by={e['id']:e for e in entries}
    if any(e.get('kind')=='unknown' or e.get('classification_required') for e in entries):raise ValueError('Prior statement contains unclassified vouchers; review its import before reserving receipts')
    if len(by)!=len(entries):raise ValueError('Duplicate voucher identities in prior statement')
    approvals=approvals or []
    if not isinstance(approvals,list):raise ValueError('Invalid CN approvals')
    approved={};release={}
    for a in approvals:
        cn=by.get(a.get('cn'));receipt=by.get(a.get('receipt'));earned=a.get('earned','')
        if not cn or cn['kind']!='posted_cn' or not receipt or receipt['kind']!='receipt':raise ValueError('Choose an actual posted CN and receipt from the prior PDF')
        cd=(cn.get('original') or cn)['date'];rd=(receipt.get('original') or receipt)['date']
        date.fromisoformat(earned)
        if not earned<rd<cd:raise ValueError('CN must be earned before the selected receipt and posted after it')
        if cn['id'] in approved or not str(a.get('reason','')).strip():raise ValueError('Each CN needs one approval with evidence; duplicate CN use is blocked')
        approved[cn['id']]=a;release.setdefault(receipt['id'],[]).append(cn)
    balance=Decimal(str(previous['opening']));rows=[]
    # Prior financial-year activity is replayed in source order for same-day transactions.
    for e in sorted(enumerate(entries),key=lambda x:((x[1].get('original') or x[1])['date'],x[0])):
        e=e[1];dt=(e.get('original') or e)['date'];credit=amount(e.get('credit'));debit=amount(e.get('debit'))
        if e['kind']=='receipt' and start<=dt<=end:
            cn_total=sum((amount(c['credit']) for c in release.get(e['id'],[])),Decimal(0))
            # Retroactive credit clears only actual pre-receipt dues. Excess stays at posting.
            adjusted=min(max(balance,Decimal(0)),cn_total);balance-=adjusted
            for cn in release.get(e['id'],[]):
                use=min(adjusted,amount(cn['credit']));approved[cn['id']]={**approved[cn['id']],'used':str(use)};adjusted-=use
            dues=max(balance,Decimal(0));cleared=min(dues,credit);available=credit-cleared
            applied=sum((Decimal(approved[c['id']]['used']) for c in release.get(e['id'],[])),Decimal(0))
            rows.append({'id':e['id'],'date':dt,'reference':e.get('reference') or e['id'],
                         'amount':str(credit),'earlier_dues':str(dues+applied),
                         'cn_adjustment':str(applied),'cleared':str(cleared),'available':str(available)})
            # Available money becomes protected; later crop invoices do not consume it.
            balance-=cleared;balance+=debit
        else:
            used=Decimal(approved.get(e['id'],{}).get('used','0'))
            balance+=debit-credit+used
    if any(a.get('receipt') not in {r['id'] for r in rows} for a in approvals):raise ValueError('Approved CN receipt must fall within the selected period')
    return {**pair,'match':match,'start':start,'end':end,'rows':rows,'approvals':approvals,'activity':entries,'cn_candidates':[e for e in entries if e['kind']=='posted_cn' and amount(e.get('credit'))>0]}

def attach(record,previous,current,start,end,approvals,selections):
    if record.get('status')!='draft':raise ValueError('Create a draft revision before changing payment history')
    plan=analyse(previous,current,start,end,approvals)
    by={r['id']:r for r in plan['rows']};sources=[]
    if not isinstance(selections,list):raise ValueError('Choose receipts to reserve')
    seen=set()
    for selection in selections:
        rid=selection.get('receipt');crop=str(selection.get('crop','')).strip();n=amount(selection.get('amount'))
        if rid not in by or rid in seen or not crop or not 0<n<=amount(by[rid]['available']):raise ValueError('Choose each receipt once, a crop and an amount within its available balance')
        seen.add(rid);row=by[rid]
        sources.append({'id':'prior-'+signature(previous)[:12]+'-'+rid,'date':row['date'],'amount':str(n),'crop':crop,'receipt':rid,'label':'Prior receipt '+row['reference']+' · '+crop+' reserved','original_amount':row['amount'],'earlier_clearance':row['cleared']})
    out=copy.deepcopy(record)
    traced={x['id'] for x in out.get('opening_sources',[]) if x.get('year_link_receipt')}
    if any(a.get('source') in traced for a in out.get('allocations',[])):raise ValueError('Review/remove existing Year Link allocations before replacing them with receipt reservations')
    newby={x['id']:x for x in sources}
    for old in out.get('reserved_sources',[]):
        if any(a.get('source')==old['id'] for a in out.get('allocations',[])) and old!=newby.get(old['id']):raise ValueError('Review/remove allocations before changing a reserved receipt')
    out['opening_sources']=[x for x in out.get('opening_sources',[]) if x['id'] not in traced]
    out['reserved_sources']=sources
    out['payment_history']={'previous':copy.deepcopy(previous),'current_signature':signature(current),'previous_signature':signature(previous),'start':start,'end':end,'approvals':copy.deepcopy(approvals),'selections':copy.deepcopy(selections),'plan':plan}
    reserve=sum((amount(x['amount']) for x in sources),Decimal(0))
    cap=max(Decimal(0),-Decimal(str(out['opening']))-reserve)
    total=sum((amount(x['amount']) for x in out['opening_sources']),Decimal(0))
    excess=max(Decimal(0),total-cap)
    # Release only unallocated metadata. Existing financial splits are preserved.
    for source in reversed(out['opening_sources']):
        used=sum((amount(a.get('amount')) for a in out.get('allocations',[]) if a.get('source')==source['id']),Decimal(0))
        trim=min(excess,max(Decimal(0),amount(source['amount'])-used))
        source['amount']=str(amount(source['amount'])-trim);excess-=trim
    if excess:
        raise ValueError('Opening credit already allocated overlaps linked receipts by '+str(excess)+'. Reduce/reassign those opening-credit allocations before linking; no saved allocation was changed.')
    out['opening_sources']=[x for x in out['opening_sources'] if amount(x['amount'])>0 or any(a.get('source')==x['id'] for a in out.get('allocations',[]))]
    out['old_dues']=str(max(Decimal(0),Decimal(str(out['opening']))+reserve))
    out['opening_dues_review_required']=True
    out['opening_dues_review']={'opening':str(out['opening']),'old_dues':out['old_dues'],'reason':'Prior receipt reservations reconciled to original statements; protected crop money excluded from later invoices.'}
    out['ledger_confirmed']=False
    validate(out)
    return out

def validate(record):
    sources=record.get('reserved_sources',[]);proof=record.get('payment_history')
    if not sources and not proof:return
    if not proof:raise ValueError('Reserved receipts require canonical prior-statement evidence')
    previous=proof['previous']
    if signature(previous)!=proof['previous_signature']:raise ValueError('Prior receipt evidence changed')
    # Current opening must continue to reconcile; later source replacements require a fresh review.
    if Decimal(str(previous['closing']))!=Decimal(str(record['opening'])):raise ValueError('Prior closing/current opening changed')
    plan=analyse(previous,{'party':record['party'],'address':record.get('address',''),'location':record.get('location',''),'opening':record['opening'],'closing':record['closing'],'entries':record['entries'],'source':record['source']},proof['start'],proof['end'],proof['approvals'])
    by={r['id']:r for r in plan['rows']};expected=[]
    for s in proof['selections']:
        rid=s['receipt'];row=by.get(rid);n=amount(s['amount'])
        if not row or not s.get('crop') or not 0<n<=amount(row['available']):raise ValueError('Reservation exceeds reviewed receipt availability')
        expected.append({'id':'prior-'+signature(previous)[:12]+'-'+rid,'date':row['date'],'amount':str(n),'crop':s['crop'],'receipt':rid,'label':'Prior receipt '+row['reference']+' · '+s['crop']+' reserved','original_amount':row['amount'],'earlier_clearance':row['cleared']})
    if expected!=sources or len({s['receipt'] for s in sources})!=len(sources):raise ValueError('Reserved receipt amount/date/crop evidence changed')

def allocation_crops(record,settings):
    sources={s['id']:s for s in record.get('reserved_sources',[])};schemes={s['id']:s for s in settings['schemes']}
    for a in record.get('allocations',[]):
        src=sources.get(a.get('source'))
        if not src:continue
        if a.get('type')=='Settlement':
            if not str(a.get('remark','')).strip():raise ValueError('Reserved-money settlement requires an explicit reason')
        elif schemes.get(a.get('scheme'),{}).get('crop')!=src['crop']:raise ValueError('Receipt reserved for '+src['crop']+'; change the reservation explicitly before using another crop')

def usage(record):
    """Physical receipt identity, independent of PDF hash or workbook IDs."""
    prefix=(exact(record.get('party')),exact(record.get('address')),exact((record.get('source') or {}).get('issuer')))
    def key(e):return prefix+((e.get('original') or e).get('date'),exact(e.get('reference') or e['id']),str(amount(e.get('credit') or e.get('original_amount'))))
    out={}
    for e in record.get('entries',[]):
        if e.get('kind')=='receipt':
            n=sum((amount(a.get('amount')) for a in record.get('allocations',[]) if a.get('source')==e['id']),Decimal(0))
            if n:out[key(e)]=(n,amount(e['credit']))
    proof=(record.get('payment_history') or {});prior={e['id']:e for e in proof.get('previous',{}).get('entries',[])}
    for s in record.get('reserved_sources',[]):
        e=prior.get(s['receipt'])
        if e:
            out[key(e)]=(amount(s['amount']),amount(e['credit'])-amount(s['earlier_clearance']))
    # Legacy traced opening sources also consume their original receipt budget.
    prior={e['id']:e for e in record.get('prior_year_link',{}).get('previous_document',{}).get('entries',[])}
    for s in record.get('opening_sources',[]):
        e=prior.get(s.get('year_link_receipt'))
        if e:
            n=sum((amount(a.get('amount')) for a in record.get('allocations',[]) if a.get('source')==s['id']),Decimal(0))
            if n:out[key(e)]=(n,amount(e['credit']))
    return out

def conflicts(record,others):
    # Keep legacy draft semantics; new reservations additionally lock their receipt budgets.
    others=list(others)
    if not record.get('reserved_sources') and not any(r.get('reserved_sources') for r in others):return
    # Keep an issued ancestor's consumption locked until a later issued revision replaces it.
    groups={}
    for r in others:
        if r.get('deleted_at') and r.get('status')!='issued':continue
        if r.get('id')==record.get('id') or r.get('lineage',r.get('id'))==record.get('lineage',record.get('id')):continue
        k=r.get('lineage') or r.get('id');groups.setdefault(k,[]).append(r)
    own=usage(record);totals={k:n for k,(n,cap) in own.items()};caps={k:cap for k,(n,cap) in own.items()}
    def cn_targets(r):
        proof=r.get('payment_history') or {}
        if not r.get('reserved_sources'):return {}
        entries={e['id']:e for e in proof['previous']['entries']}
        prefix=(exact(r.get('party')),exact(r.get('address')),exact((r.get('source') or {}).get('issuer')))
        out={}
        for a in proof['approvals']:
            cn=entries[a['cn']];receipt=entries[a['receipt']]
            key=prefix+(cn['date'],exact(cn.get('reference') or cn['id']),str(amount(cn['credit'])))
            out[key]=(receipt['date'],exact(receipt.get('reference') or receipt['id']))
        return out
    targets=cn_targets(record)
    for rows in groups.values():
        current=max(rows,key=lambda r:(r.get('saved_at',''),r.get('revision',0)))
        issued=[r for r in rows if r.get('status')=='issued']
        candidates=[current]
        if issued:candidates.append(max(issued,key=lambda r:(r.get('issued_at',''),r.get('revision',0))))
        combined={}
        for r in candidates:
            for key,target in cn_targets(r).items():
                if key in targets and targets[key]!=target:raise ValueError('This late-posted CN already releases another original receipt; duplicate CN release is blocked.')
            for k,(n,cap) in usage(r).items():
                prev=combined.get(k,(Decimal(0),cap));combined[k]=(max(prev[0],n),min(prev[1],cap))
        for k,(n,cap) in combined.items():
            if k in own:
                totals[k]=totals.get(k,Decimal(0))+n;caps[k]=min(caps[k],cap)
    if any(n>caps[k] for k,n in totals.items()):raise ValueError('Original receipt is already reserved/allocated in another saved calculation. Review that allocation first; duplicate use is blocked.')
