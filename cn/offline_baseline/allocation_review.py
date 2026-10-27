"""Reviewed segment CD funding and release of unused direct CD allocations.

The financial engine remains the authority. No dates, product entitlement rules,
ABS excess routing or rounding policies are changed here.
"""
import copy,hashlib
from decimal import Decimal,localcontext,ROUND_CEILING
from engine import compute,effective_settings,D,validate_input_limits,validate_scheme
from store import dump


def plain(value):
    text=format(value,'f')
    return text.rstrip('0').rstrip('.') if '.' in text else text


def kept_amount(amount,used):
    # Retain enough funding to preserve the engine's full-precision entitlement.
    # Ordinary rupee amounts retain at most one extra paisa, never round down.
    scale=max(2,-amount.as_tuple().exponent)
    return min(amount,used.quantize(Decimal(1).scaleb(-scale),rounding=ROUND_CEILING))


def cd_work(result,allocation):
    return next((w for g in result.get('groups',[]) for w in g['CD_work'] if w['allocation']==allocation),None)


def entitlements(result):
    return [(c['key'],c['rounded']) for c in result['CNs']]


def review_allocation(store,payload,apply=False):
    with localcontext() as ctx:
        ctx.prec=100
        r=store.get(payload['id']);cfg=store.settings()
        if r.get('deleted_at') or r.get('status')!='draft':
            raise ValueError('Restore the party or create a draft revision before allocating payments')
        if payload.get('revision')!=r['revision']:
            raise ValueError('Calculation changed; reopen the allocation preview')
        operation=payload.get('operation')
        if operation not in ('cd-group','cd-release'):raise ValueError('Choose a supported payment operation')
        args={k:payload.get(k,'') for k in ('operation','crop','scheme','source','amount','target')}
        expected=hashlib.sha256(dump({'record':r,'settings':cfg,'selection':args}).encode()).hexdigest()
        if apply and payload.get('expected')!=expected:
            raise ValueError('Calculation or settings changed; reopen the allocation preview')
        before=compute(r,cfg);effective=effective_settings(r,cfg)
        candidate=copy.deepcopy(r)
        plan={'expected':expected,'operation':operation,'previous_CN':before['new_CN_total']}
        if operation=='cd-release':
            row=next((a for a in r.get('allocations',[]) if a['id']==payload.get('target')),None)
            if not row or row.get('type')!='CD':raise ValueError('Choose a direct CD allocation; ABS excess keeps its first-CD rule')
            work=cd_work(before,row['id'])
            if not work:raise ValueError('Review the CD allocation before releasing its funding')
            amount=D(row['amount']);keep=kept_amount(amount,D(work['eligible_payment']));released=amount-keep
            if released<=0:raise ValueError('No releasable unused CD funding remains')
            candidate['allocations']=[{**a,'amount':plain(keep)} if a['id']==row['id'] else a for a in r['allocations'] if a['id']!=row['id'] or keep>0]
            after=compute(candidate,cfg)
            if entitlements(before)!=entitlements(after):raise ValueError('Release changes benefit entitlement; review the allocation manually')
            plan.update(target=row['id'],scheme=row['scheme'],source=row['source'],original_date=work['original_date'],assigned=amount,used=work['eligible_payment'],unused=work['unused'],retained=keep,released=released,percent=work['percent'])
        else:
            groups={g['scheme']:g for g in before.get('groups',[])}
            schemes=[s for s in effective['schemes'] if not s.get('deleted_at') and not s.get('mapping_placeholder') and 'CD' in s.get('benefits',[]) and s.get('season')==r.get('season') and s['id'] in groups and D(groups[s['id']]['net'])>0 and (not payload.get('crop') or s['crop']==payload['crop'])]
            sources=[{**s,'remaining':s['available']-sum((D(a.get('amount') or 0) for a in r.get('allocations',[]) if a.get('source')==s['id']),D(0))} for s in before['sources']]
            if payload.get('options'):
                if apply:raise ValueError('Preview an amount before applying')
                return {'schemes':[{'id':s['id'],'name':s['name'],'crop':s['crop'],'segment':s['segment']} for s in schemes],'sources':sources}
            sc=next((s for s in schemes if s['id']==payload.get('scheme')),None)
            if not sc:raise ValueError('Choose one eligible sold segment/scheme; different schemes are kept separate')
            errors=validate_scheme(sc,True)
            if errors:raise ValueError('Review CD scheme setup: '+'; '.join(errors))
            source=next((s for s in sources if s['id']==payload.get('source')),None)
            amount=D(payload.get('amount') or 0)
            if not source or amount<=0:raise ValueError('Select a receipt and enter a positive amount')
            if amount>source['remaining']:raise ValueError('Amount exceeds this receipt’s remaining availability after old dues and other splits')
            # Top up the last existing CD split for this same receipt/segment.
            # Creating a new sorted ID could otherwise jump ahead of its own
            # funding and report already-funded capacity as a new requirement.
            matches=[a for a in r['allocations'] if a.get('type')=='CD' and a.get('source')==source['id'] and a.get('scheme')==sc['id'] and cd_work(before,a['id'])]
            order=[w['allocation'] for w in groups[sc['id']]['CD_work']]
            existing=max(matches,key=lambda a:order.index(a['id'])) if matches else None
            old_amount=D(existing['amount']) if existing else D(0)
            old_used=D(cd_work(before,existing['id'])['eligible_payment']) if existing else D(0)
            aid=existing['id'] if existing else 'cd35-'+expected[:24]
            row=next((a for a in candidate['allocations'] if a['id']==aid),None)
            if row is None:
                row={'id':aid,'source':source['id'],'scheme':sc['id'],'product':'','type':'CD'}
                if r.get('manual_order'):
                    row['order']=str(max((D(a.get('order') or 0) for a in r['allocations'] if a.get('type')=='CD'),default=D(0))+1)
                candidate['allocations'].append(row)
            row['amount']=plain(old_amount+amount);validate_input_limits(candidate,cfg)
            full=compute(candidate,cfg);work=cd_work(full,aid)
            if not work:raise ValueError('This payment/destination needs correction before CD can be allocated')
            added=[x for x in full['issues'] if x not in before['issues']]
            if added:raise ValueError('Review allocation: '+'; '.join(added))
            incremental_used=max(D(0),min(amount,D(work['eligible_payment'])-old_used))
            keep=kept_amount(amount,incremental_used);released=amount-keep
            if keep:row['amount']=plain(old_amount+keep)
            elif existing:row['amount']=plain(old_amount)
            else:candidate['allocations'].pop()
            after=compute(candidate,cfg)
            if entitlements(full)!=entitlements(after):raise ValueError('Preview changed benefit entitlement; review this allocation manually')
            products=[{'product_id':p['product_id'],'product':p['product'],'regular_net':p['regular_net'],'unit':p['unit'],'packing_kg':p['packing_kg'],'CD_CN':sum((D(b['CN']) for b in p['benefits'] if b['benefit']=='CD'),D(0))} for p in after['product_CNs'] if p['scheme']==sc['id']]
            affected=[]
            for a in r['allocations']:
                if a.get('type')!='CD':continue
                old=cd_work(before,a['id']);new=cd_work(after,a['id'])
                if old and new and D(new['unused'])>D(old['unused']):affected.append({'allocation':a['id'],'source':a['source'],'unused':new['unused']})
            plan.update(scheme=sc['id'],scheme_name=sc['name'],crop=sc['crop'],segment=sc['segment'],source=source['id'],original_date=source['date'],requested=amount,used=incremental_used,unused=amount-incremental_used,retained=keep,released=released,remaining=source['remaining']-keep,percent=work['percent'],slab=work['slab'],period=work['period'],CD=incremental_used*D(work['percent'])/100,products=products,affected=affected,allocation_id=aid)
        validate_input_limits(candidate,cfg)
        plan.update(new_CN=after['new_CN_total'],issues=after['issues'])
        if apply:
            if operation=='cd-group' and not plan['retained']:raise ValueError('This segment needs no additional CD funding; choose another destination')
            return store.save(candidate)
        return plan
