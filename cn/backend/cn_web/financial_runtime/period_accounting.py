"""Dated period view and conservative receipt clearance; original vouchers stay intact."""
from decimal import Decimal
import re
import hashlib
import json
from datetime import datetime
D=lambda n: Decimal(str(n or 0))

def printed_splits(entry):
    """Read only preserved PDF lines. No narration inference or voucher mutation."""
    original=entry.get('original') or entry
    rows=[];invalid=False
    for line in original.get('source_lines',[]):
        text=line.get('text','').strip()
        if not re.match(r'^(Agst Ref|New Ref|Advance|On Account)\b',text,re.I):continue
        match=re.fullmatch(r'(Agst Ref|New Ref)\s+(\S+)(?:\s+(\d{1,2}-[A-Za-z]{3}-\d{2,4}))?\s+([\d,]+\.\d{2})\s+(Dr|Cr)',text,re.I)
        if not match:invalid=True;continue
        kind,ref,dt,n,side=match.groups()
        if dt:
            try:dt=datetime.strptime(dt,'%d-%b-%Y' if len(dt.split('-')[-1])==4 else '%d-%b-%y').date().isoformat()
            except ValueError:invalid=True;continue
        rows.append(dict(type=kind.lower(),reference=ref,date=dt,amount=str(D(n.replace(',',''))),side=side.lower()))
    if not rows:return [], ['Unparsed bill allocation requires review'] if invalid else []
    # Mixed debit/credit reallocations cannot be interpreted as ordinary cash splits.
    if invalid or any(x['side']!='cr' for x in rows) or sum((D(x['amount']) for x in rows),D(0))!=D(entry.get('credit')):
        return [],['Bill allocation totals/directions require review; chronological fallback used']
    return rows,[]

def accounting_evidence(record,period):
    entries=[]
    for e in record.get('entries',[]):
        original=e.get('original') or e
        entries.append({'id':e['id'],'date':original['date'],'kind':e['kind'],
                        'reference':e.get('reference'),'debit':str(e.get('debit') or 0),
                        'credit':str(e.get('credit') or 0),'settlement_reference':e.get('settlement_reference'),
                        'source_lines':original.get('source_lines',[])})
    proof={'period':period,'opening':str(record['opening']),'entries':entries,'reserved':record.get('reserved_sources',[])}
    return hashlib.sha256(json.dumps(proof,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def view(record, period):
    start,end=period['start'],period['end']; cutoff=period['cutoff']
    entries=record.get('entries',[])
    ordered=sorted(enumerate(entries),key=lambda x:((x[1].get('original') or x[1])['date'],x[0]))
    evidence=accounting_evidence(record,period)
    review=record.get('accounting_review') or {}
    approved=review.get('evidence')==evidence and len(str(review.get('reason','')).strip())>=12
    same_days={}
    for _,e in ordered:
        dt=(e.get('original') or e)['date']
        if dt<=cutoff and D(e.get('credit'))>0 and e['kind'] in ('receipt','posted_cn'):same_days.setdefault(dt,set()).add(e['kind'])
    same_days={dt for dt,kinds in same_days.items() if len(kinds)==2}
    if approved:
        # Move only CN/receipt slots. Dates and other voucher positions are intact.
        for dt in same_days:
            mode=review.get('same_day_order',{}).get(dt)
            if mode not in ('source','cn_first','receipt_first'):approved=False;break
        if approved:
            for dt in same_days:
                mode=review['same_day_order'][dt]
                if mode=='source':continue
                slots=[i for i,(_,e) in enumerate(ordered) if (e.get('original') or e)['date']==dt and e['kind'] in ('receipt','posted_cn')]
                first='posted_cn' if mode=='cn_first' else 'receipt'
                values=sorted((ordered[i] for i in slots),key=lambda pair:pair[1]['kind']!=first)
                for i,value in zip(slots,values):ordered[i]=value
    opening=D(record['opening']); balance=opening; period_open=opening; totals={}; rows=[]
    reserved=sum((D(s['amount']) for s in record.get('reserved_sources',[])),D(0))
    debts=[{'reference':'__opening__','amount':max(opening+reserved,D(0)),'old':True}]
    carried={'available':max(-opening-reserved,D(0))}
    advances=[carried]; sources=[]; warnings=[];settlements=[];review_items=[]
    def require_review(kind,message,entry=None,dt=None):
        item={'kind':kind,'message':message}
        if entry:item['entry']=entry
        if dt:item['date']=dt
        if item not in review_items:review_items.append(item)
        if message not in warnings:warnings.append(message)
    for dt in sorted(same_days):require_review('same_day_order','Confirm receipt/CN order on '+dt,dt=dt)
    def clear(n,reference=None,old_only=False):
        for debt in debts:
            if reference and debt['reference']!=reference:continue
            if old_only and not debt['old']:continue
            used=min(n,debt['amount']);debt['amount']-=used;n-=used
        return n
    for _,e in ordered:
        dt=(e.get('original') or e)['date']; debit,credit=D(e.get('debit')),D(e.get('credit'))
        if dt>cutoff:continue
        if dt<start:period_open+=debit-credit
        if start<=dt<=end:
            rows.append(e['id']); totals.setdefault(e['kind'],{'debit':D(0),'credit':D(0)})
            totals[e['kind']]['debit']+=debit;totals[e['kind']]['credit']+=credit
        balance+=debit-credit
        ref=e.get('settlement_reference')
        # Only explicit structured references matching a real invoice are reliable.
        if ref and len([d for d in debts if d['reference']==ref])!=1:
            require_review('reference','Unresolved/ambiguous settlement reference: '+str(ref),e['id']);ref=None
        if debit:
            remaining=debit
            if dt<start:
                for a in advances:
                    used=min(remaining,a['available']);a['available']-=used;remaining-=used
            debts.append({'reference':e.get('reference') or e['id'],'amount':remaining,'old':dt<start})
        if not credit:continue
        splits,split_warnings=printed_splits(e)
        if not ref:
            for w in split_warnings:require_review('printed_split',str(e.get('reference') or e['id'])+': '+w,e['id'])
        if ref:splits=[] # An explicitly reviewed single reference overrides printed splits.
        def settle_printed():
            old_used=D(0);unmatched=D(0)
            for split in splits:
                n=D(split['amount']);target=split['reference']
                matches=[d for d in debts if d['reference']==target]
                prior=split.get('date') and split['date']<str(record.get('source',{}).get('report_start') or start)
                if split['type']=='agst ref' and len(matches)==1:
                    debt=matches[0];used=min(n,debt['amount']);debt['amount']-=used
                    if debt['old']:old_used+=used
                    unmatched+=n-used;left=n-used
                    destination='earlier invoice' if debt['old'] else 'selected-period invoice'
                    if left:require_review('reference','Allocation exceeds remaining bill '+target,e['id'])
                elif split['type']=='agst ref' and prior:
                    debt=debts[0];used=min(n,debt['amount']);debt['amount']-=used;old_used+=used;unmatched+=n-used;left=n-used
                    destination='opening outstanding'
                else:
                    if split['type']=='agst ref':require_review('reference','Unresolved/ambiguous printed bill '+target,e['id'])
                    # A credit-note New Ref remains a posting-date credit; unknown
                    # invoice refs use conservative FIFO, never invented targets.
                    before=sum((d['amount'] for d in debts if d['old']),D(0))
                    left=clear(n,old_only=dt>=start)
                    old_used+=before-sum((d['amount'] for d in debts if d['old']),D(0));unmatched+=left
                    destination='chronological fallback'
                settlements.append({'entry':e['id'],**split,'posting_date':dt,'applied_amount':str(n-left),'unconsumed_amount':str(left),'destination':destination})
            return old_used,unmatched
        if e['kind']=='receipt':
            old_before=sum((d['amount'] for d in debts if d['old']),D(0))
            if splits:
                split_old,unused=settle_printed()
            else:unused=clear(credit,ref,old_only=dt>=start and not ref)
            if dt>=start:
                old_after=sum((d['amount'] for d in debts if d['old']),D(0))
                unused=credit-(old_before-old_after)
            src={'id':e['id'],'date':dt,'amount':credit,'available':unused,'old_dues_cleared':credit-unused,'opening':False}
            sources.append(src)
            if dt<start:advances.append(src)
        else:
            # Credits affect outstanding on their posting date. They never restore
            # any previously consumed receipt. Freight remains accounting-only.
            if splits:_,leftover=settle_printed()
            else:leftover=clear(credit,ref,old_only=dt>=start and not ref)
            if dt<start:carried['available']+=leftover
    for src in sources:src['old_dues_cleared']=src['amount']-src['available']
    closing=period_open+sum((v['debit']-v['credit'] for v in totals.values()),D(0))
    return {'start':start,'end':end,'cutoff':cutoff,'opening':str(period_open),'closing':str(closing),
            'totals':{k:{f:str(n) for f,n in v.items()} for k,v in totals.items()},'entry_ids':rows,
            'settlements':settlements,
            'review_items':review_items,'review_evidence':evidence,'review_required':bool(review_items) and not approved,
            'accounting_review':review if approved else None,
            'sources':[{k:str(v) if isinstance(v,Decimal) else v for k,v in s.items()} for s in sources],
            'untraced_opening_remaining':str(carried['available']),
            'old_dues_remaining':str(sum((d['amount'] for d in debts if d['old']),D(0))), 'warnings':warnings}

def payment_sources(record, fallback):
    p=record.get('period_accounting')
    if not p:return fallback,None
    known={s['id']:s for s in p['sources']}
    out=[];opening_left=D(p.get('untraced_opening_remaining',0))
    opening_ids={x['id'] for x in record.get('opening_sources',[])}
    for s in sorted(fallback,key=lambda s:(s.get('date') or '',s['id'])):
        if s['id'] in known:
            out.append({**s,**known[s['id']],**{k:D(known[s['id']][k]) for k in ('amount','available','old_dues_cleared')}})
        elif s.get('reserved'):
            out.append({**s,'available':D(s['amount']),'old_dues_cleared':D(0)})
        elif s.get('opening') or s['id'] in opening_ids:
            available=min(opening_left,D(s['amount']));opening_left-=available
            out.append({**s,'available':available,'old_dues_cleared':D(s['amount'])-available})
        else:
            out.append({**s,'available':D(0),'old_dues_cleared':D(0),'outside_cutoff':True})
    return sorted(out,key=lambda s:(s.get('date') or '',s['id'])),D(p['old_dues_remaining'])
