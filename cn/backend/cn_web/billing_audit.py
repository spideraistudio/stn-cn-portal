"""Read-only billing comparisons. Never writes financial settings or vouchers."""
import copy
import hashlib
import json
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from .security import AuthError
from .data_store import fields
from .product_mapping import plan, compatible


def key(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,default=str,separators=(',',':')).encode()).hexdigest()


def norm(value):
    return ' '.join(str(value or '').upper().split())


def decimal(value):
    try:
        n=Decimal(str(value))
        if not n.is_finite() or abs(n)>Decimal('1e15'):raise ValueError()
        return n
    except (ValueError,InvalidOperation):raise AuthError('Invalid billing number',400)


def rate_in_unit(source, target):
    """Compare quoted rates, without a lossy per-kg round trip.

    A same-unit quote needs no packing conversion. For different units, multiply
    before dividing, then use the precision of the printed quotes (at least
    paise). Bulk quantities must not magnify a sub-paise conversion residue.
    This never rewrites the source rate, amount or saved packing.
    """
    rate=decimal(source['rate'])
    if source['unit']==target['unit']:
        return rate
    places=max(2,-rate.as_tuple().exponent,-decimal(target['rate']).as_tuple().exponent)
    with localcontext() as ctx:
        ctx.prec=max(50,places+35)
        converted=rate*decimal(target['factor'])/decimal(source['factor'])
        return converted.quantize(Decimal(1).scaleb(-places),rounding=ROUND_HALF_UP)


def day(value):
    try:
        if not isinstance(value,str) or date.fromisoformat(value).isoformat()!=value:raise ValueError()
    except ValueError:raise AuthError('Use an ISO billing date (YYYY-MM-DD)',400)
    return value


def recorded_states(cfg, documents, meta, settings, records):
    """Display choices only; never rewrite stored state labels or source evidence."""
    values=[r['state'] for r in cfg['rates']]
    values += [d.get('state','') for d in documents]
    values += [meta.get('state','')]
    values += [r.get('state','') for r in records]
    values += [v for scheme in settings.get('schemes',[]) for v in scheme.get('states',[])]
    unique={}
    for value in values:
        if isinstance(value,str) and norm(value) and norm(value) != 'ALL':
            unique.setdefault(norm(value),' '.join(value.split()))
    return sorted(unique.values(),key=norm)


def canonical_rates(rates, existing, states):
    # Existing rows retain their exact spelling. New/edited rows reuse recorded
    # case/spacing variants; no fuzzy merging of distinct stored states.
    labels={norm(v):v for v in states}
    return [copy.deepcopy(r) if r in existing else {**r,'state':labels.get(norm(r.get('state')), ' '.join(str(r.get('state','')).split()))} for r in rates]


def empty():return {'rates':[],'matches':{},'sources':[]}


def validate(value,catalogue):
    fields(value,{'rates','matches','sources'},{'reviews'})
    reviews=value.get('reviews',{})
    if not isinstance(reviews,dict) or len(reviews)>10000:raise AuthError('Invalid billing reviews',400)
    for rid,review in reviews.items():
        if not isinstance(rid,str) or len(rid)!=64:raise AuthError('Invalid billing review identity',400)
        fields(review,{'status','reason','evidence'})
        if review['status'] not in ('mistake','approved_exception','not_applicable') or not isinstance(review['reason'],str) or not review['reason'].strip() or len(review['reason'])>2000 or not isinstance(review['evidence'],str) or len(review['evidence'])!=64:raise AuthError('Choose a review status and enter a reason',400)
    products={p['id']:p for p in catalogue}
    if not isinstance(value['rates'],list) or len(value['rates'])>10000:raise AuthError('Invalid approved rates',400)
    prior={}
    for r in value['rates']:
        fields(r,{'state','product','start','end','unit','rate'})
        if not isinstance(r['state'],str) or not norm(r['state']) or len(r['state'])>100:raise AuthError('State is required for every rate',400)
        if r['product'] not in products or r['unit'] not in ('kg','packet'):raise AuthError('Select a saved product and rate unit',400)
        if day(r['start'])>day(r['end']) or decimal(r['rate'])<=0:raise AuthError('Invalid rate period or amount',400)
        identity=(norm(r['state']),r['product'])
        if any(r['start']<=b and r['end']>=a for a,b in prior.get(identity,[])):raise AuthError('Approved rate periods overlap for this state/product',409)
        prior.setdefault(identity,[]).append((r['start'],r['end']))
    if not isinstance(value['matches'],dict) or len(value['matches'])>10000:raise AuthError('Invalid return selections',400)
    for rid,parts in value['matches'].items():
        if not isinstance(rid,str) or len(rid)!=64 or not isinstance(parts,list) or not parts or len(parts)>100:raise AuthError('Invalid return selection',400)
        seen=set()
        for part in parts:
            fields(part,{'sale','qty'})
            if not isinstance(part['sale'],str) or len(part['sale'])!=64 or part['sale'] in seen or decimal(part['qty'])<=0:raise AuthError('Invalid original bill quantity',400)
            seen.add(part['sale'])
    if not isinstance(value['sources'],list) or len(value['sources'])>1000:raise AuthError('Too many billing sources',400)
    for ref in value['sources']:
        if 'web_ledger_id' in ref:fields(ref,{'web_ledger_id'})
        else:
            fields(ref,{'web_file_id','web_document_index'})
            if type(ref['web_document_index']) is not int or ref['web_document_index']<0:raise AuthError('Invalid billing document index',400)
    return value


def lines(documents,state):
    result=[];seen=Counter();products={p['id']:p for p in state['catalogue']}
    warnings=[]
    for doc in documents:
        identity=[norm(doc.get(k)) for k in ('party','location','state')]
        mapping=plan(doc,state);local=Counter()
        warnings.extend(str(w) for w in doc.get('warnings',[]))
        for ei,e in enumerate(doc.get('entries',[])):
            if e.get('kind') not in ('sale','return'):continue
            # Content identity ignores filenames/PDF bytes, retains multiplicity
            # within each statement. Differing overlapping postings are NOT merged.
            sig=key([identity,e.get('date'),norm(e.get('reference')),e['kind'],
                     [[norm(i.get('name')),i.get('unit'),str(decimal(i.get('qty',0)).normalize()),str(decimal(i.get('rate',0)).normalize()),str(decimal(i.get('amount',0)).normalize())] for i in e.get('items',[])]])
            local[sig]+=1
            if local[sig]<=seen[sig]:continue
            items=e.get('items',[]) or [{}]
            for ii,item in enumerate(items):
                pid=mapping.get(f'{ei}:{ii}',{}).get('product_id') if item else None
                # A reviewed canonical ledger mapping takes precedence.
                if item.get('mapping_confirmed') and item.get('product') in products and compatible(item,products[item['product']]):pid=item['product']
                qty=decimal(item.get('qty',0));rate=decimal(item.get('rate',0))
                pack=decimal(products[pid]['packing_kg']) if pid else Decimal(1)
                unit=item.get('unit');factor=pack if unit=='packet' else Decimal(1)
                good=bool(pid and qty>0 and rate>0 and unit in ('kg','packet') and factor>0)
                result.append({'id':key([sig,local[sig],ii]),'party':doc.get('party',''),'location':doc.get('location',''),'state':doc.get('state',''),
                    'identity':identity,'product':pid,'name':item.get('name','Missing product lines'),'date':day(e['date']),
                    'reference':str(e.get('reference','')),'kind':e['kind'],'qty':str(qty),'unit':unit or '',
                    'rate':str(rate),'amount':str(decimal(item.get('amount',0))), 'kg':str(qty*factor),'per_kg':str(rate/factor) if factor else '0',
                    'factor':str(factor),'valid':good,'filename':doc.get('audit_filename','Saved ledger'),
                    'packing_kg':str(pack) if pid else None,'mapping_reason':mapping.get(f'{ei}:{ii}',{}).get('reason',''),'comparison_basis':'','status':'','expected_rate':None,'difference':None,'candidates':[],'allocations':[]})
        seen|=local
    # Same invoice/product/date with conflicting numbers needs explicit source review.
    groups={}
    for row in result:
        k=key([row['identity'],row['date'],norm(row['reference']),row['kind'],row['product'] or norm(row['name'])])
        groups.setdefault(k,[]).append(row)
    for group in groups.values():
        if len(group)>1:
            for row in group:row['valid']=False;row['status']='Duplicate or conflicting invoice lines — review source'
    return sorted(result,key=lambda r:(r['date'],r['kind']=='return',r['id'])),list(dict.fromkeys(warnings))


def run(documents,state,start,end,matches=None,strict=False):
    if day(start)>day(end):raise AuthError('Checking start must precede end',400)
    cfg=state.get('billing_audit',empty());validate(cfg,state['catalogue'])
    rows,warnings=lines(documents,state);choices=cfg['matches'] if matches is None else matches
    validate({**cfg,'matches':choices},state['catalogue'])
    byid={r['id']:r for r in rows};sales=[r for r in rows if r['kind']=='sale'];used={r['id']:Decimal(0) for r in sales}
    uncertain=set();applied=set()
    for r in rows:
        if r['date']>end:continue
        if not r['valid']:
            problems=[]
            if not r['product']:problems.append('Product mapping required: '+r['mapping_reason'])
            if decimal(r['qty'])<=0:problems.append('Printed quantity must be positive')
            if decimal(r['rate'])<=0:problems.append('Printed rate must be positive')
            if r['unit'] not in ('kg','packet'):problems.append('Printed unit is missing or unsupported')
            r['status']=r['status'] or '; '.join(problems) or 'Saved packing must be positive'
            r['comparison_basis']='Not compared: '+r['status']
            if r['kind']=='return':uncertain.add(key(r['identity']))
            continue
        if r['kind']=='sale':
            product_rates=[a for a in cfg['rates'] if a['product']==r['product']]
            state_rates=[a for a in product_rates if norm(a['state'])==norm(r['state']) and norm(r['state'])]
            rates=[a for a in state_rates if a['start']<=r['date']<=a['end']]
            # An explicitly saved ALL rate is a fallback, never a guessed state.
            if not rates:rates=[a for a in product_rates if norm(a['state'])=='ALL' and a['start']<=r['date']<=a['end']]
            if not rates:
                if not product_rates:reason='No approved rate saved for mapped product '+str(r['product'])
                elif not norm(r['state']):reason='Statement state is missing; no applicable ALL-state rate'
                elif not state_rates and not any(norm(a['state'])=='ALL' for a in product_rates):reason='No approved rate for statement state '+r['state']
                else:reason='No approved rate effective on '+r['date']
                r['status']=reason
                r['comparison_basis']='Not compared: '+reason+'; saved periods: '+('; '.join(f"{a['state']} {a['start']} to {a['end']}: {a['rate']} / {a['unit']}" for a in product_rates) or 'none')
                continue
            approved=rates[0];r['comparison_basis']=f"Mapped product {r['product']}; statement state {r['state'] or 'missing'}; approved {approved['state']} rate: {approved['rate']} / {approved['unit']} ({approved['start']} to {approved['end']})"
            p=next(p for p in state['catalogue'] if p['id']==r['product'])
            expected=rate_in_unit({**approved,'factor':p['packing_kg'] if approved['unit']=='packet' else '1'},r)
            if approved['unit']!=r['unit']:r['comparison_basis']+='; packing conversion rounded to quoted rate precision (at least 2 decimal places)'
            r['expected_rate']=str(expected);r['difference']=str((decimal(r['rate'])-expected)*decimal(r['qty']))
            r['status']='Rate matches' if abs(decimal(r['difference']))<=Decimal('.01') else 'Billing rate mismatch'
            continue
        candidates=[a for a in sales if a['valid'] and a['identity']==r['identity'] and a['product']==r['product'] and a['date']<=r['date']]
        r['candidates']=[{'sale':a['id'],'date':a['date'],'reference':a['reference'],'rate':a['rate'],'unit':a['unit'],'remaining_qty':str(max(Decimal(0),decimal(a['kg'])-used[a['id']])/decimal(r['factor'])),'filename':a['filename']} for a in candidates]
        parts=choices.get(r['id'])
        # Reuse ledger_audit's earlier-supply low/high comparison rules. This
        # compares rate evidence only; it does not select/consume any invoice.
        if not parts:
            if not candidates:
                r['status']='Original sale required — rate not verified'
                r['comparison_basis']='Not compared: no earlier matching supply with valid mapping, packing and units'
            else:
                low=min(rate_in_unit(a,r) for a in candidates)
                high=max(rate_in_unit(a,r) for a in candidates)
                actual=decimal(r['rate']);qty=decimal(r['qty'])
                r['supply_rate_min']=str(low);r['supply_rate_max']=str(high)
                r['possible_excess_min']=str(qty*max(Decimal(0),actual-high))
                r['possible_excess_max']=str(qty*max(Decimal(0),actual-low))
                r['comparison_basis']='Earlier matching printed supply rates, converted to return unit; no original invoice or quantity allocation inferred'
                if any(a['unit']!=r['unit'] for a in candidates):r['comparison_basis']+='; packing conversion rounded to quoted rate precision (at least 2 decimal places)'
                r['invoice_match_confirmed']=False
                if low==high:
                    r['expected_rate']=str(low);r['difference']=str((actual-low)*qty)
                    r['status']='Return rate above supply' if actual>high else 'Return rate below supply' if actual<low else 'Return rate matches earlier supply'
                elif actual>high:
                    r['status']='Return rate above supply'
                    r['expected_rate']=f'{low} to {high}'
                elif actual>low:
                    r['status']='Mixed supply rates — review return'
                    r['expected_rate']=f'{low} to {high}'
                    r['requires_original_bill']=True
                else:
                    r['status']='Return rate does not exceed earlier supply'
                    r['expected_rate']=f'{low} to {high}'
                r['comparison_basis']+='; invoice identity and remaining quantity are not verified'
            uncertain.add(key([r['identity'],r['product']]));continue
        chosen=[];problem=''
        for part in parts:
            a=byid.get(part['sale']);q=decimal(part['qty'])*decimal(r['factor'])
            if not a or a not in candidates:problem='Original sale missing or incompatible';break
            if used[a['id']]+q>decimal(a['kg']):problem='Return exceeds remaining billed quantity';break
            chosen.append((a,q))
        if sum((q for a,q in chosen),Decimal(0))!=decimal(r['kg']):problem=problem or 'Split quantities must equal returned quantity'
        if problem:
            if strict and r['id'] in choices:raise AuthError(problem,409)
            r['status']=problem;uncertain.add(key([r['identity'],r['product']]));continue
        r['comparison_basis']='Actual printed rate of explicitly selected original bill(s), not the current scheme or approved rate'
        if any(a['unit']!=r['unit'] for a,q in chosen):r['comparison_basis']+='; packing conversion rounded to quoted rate precision (at least 2 decimal places)'
        applied.add(r['id']);expected=Decimal(0);mismatch=False
        for a,q in chosen:
            used[a['id']]+=q
            er=rate_in_unit(a,r)
            return_qty=q/decimal(r['factor'])
            delta=(decimal(r['rate'])-er)*return_qty
            mismatch=mismatch or abs(delta)>Decimal('.01');expected+=er*return_qty
            r['allocations'].append({'sale':a['id'],'reference':a['reference'],'date':a['date'],'qty':str(q/decimal(r['factor'])),'expected_rate':str(er),'difference':str(delta)})
        # Each split is compared independently; offsetting errors cannot cancel.
        r['expected_rate']=str(expected/decimal(r['qty'])) if len(chosen)==1 else 'See original bills'
        r['difference']=str(decimal(r['rate'])*decimal(r['qty'])-expected)
        r['status']='Return rate mismatch' if mismatch else 'Return rate matches original bill'
        if key([r['identity'],r['product']]) in uncertain or key(r['identity']) in uncertain:r['status']+=' · prior return unresolved; quantity not verified'
    if strict and set(choices)-applied:raise AuthError('Saved selection is stale or outside loaded evidence; reload the original statements',409)
    visible=[r for r in rows if start<=r['date']<=end]
    for r in visible:
        if r['valid'] and abs(decimal(r['qty'])*decimal(r['rate'])-decimal(r['amount']))>Decimal('.01'):
            r['status']+=' · printed quantity × rate differs from item amount; review discounts/taxes'
    for r in visible:
        matches=('Rate matches','Return rate matches original bill','Return rate matches earlier supply','Return rate does not exceed earlier supply')
        r['attention']=r['status'] not in matches
        r['comparison_checked']=r['expected_rate'] is not None
        r['unchecked_reason']=r['status'] if not r['comparison_checked'] else ''
        r['issue_category']=r['status'].split(' · ')[0] if r['comparison_checked'] else 'Comparison not completed'
        proof=key([r,cfg['rates'],choices])
        r['review_evidence']=proof
        review=cfg.get('reviews',{}).get(r['id'])
        r['review']=review if review and review['evidence']==proof else None
    return {'rows':visible,'warnings':warnings,'evidence':key(rows),'notes':[
        'Audit only: no bill, CN scheme, allocation or frozen history is changed.',
        'Quantity checks cover only loaded statements and included saved ledgers. Add earlier-year PDFs and all prior returns.',
        'Original invoice references are not reliably extracted by this PDF format. Ambiguous rate evidence requires explicit original-bill selection; no FIFO or averaging.',
        'Same-unit printed rates are compared directly. Cross-unit packing conversions use quoted rate precision (at least 2 decimal places); original printed evidence is retained.',
        'Differences are quantity × rate differences before separately posted taxes/discounts. A one-paise line tolerance is used for approved and explicitly matched lines.'],
        'counts':{'checked':len(visible),'attention':sum(r['attention'] for r in visible),'compared':sum(r['comparison_checked'] for r in visible),'unchecked':sum(not r['comparison_checked'] for r in visible)}}
