"""Reviewed, reversible ABS product distribution; engine formulas stay authoritative."""
import copy,uuid
from decimal import Decimal,localcontext,ROUND_FLOOR
from engine import compute,effective_settings,validate_input_limits,validate_scheme,payment_work,abs_booking_allowed,unit_qty,D

def plain(value):
    text=format(value,'f')
    return text.rstrip('0').rstrip('.') if '.' in text else text

def preview(record,settings,*,crop='',scheme='',source='',amount='',replace_id='',approved=None,remark=None,options=False):
    with localcontext() as ctx:
        ctx.prec=100
        if record.get('status','draft')!='draft':raise ValueError('Create a draft revision before distributing ABS')
        base=copy.deepcopy(record);removed=None
        if replace_id:
            removed=next((a for a in base.get('allocations',[]) if a.get('id')==replace_id),None)
            if not removed or removed.get('type')!='ABS':raise ValueError('Choose an existing ABS allocation to distribute')
            base['allocations']=[a for a in base['allocations'] if a['id']!=replace_id]
        validate_input_limits(base,settings)
        cfg=effective_settings(base,settings);result=compute(base,settings)
        schemes={s['id']:s for s in cfg['schemes']};products={p['id']:p for p in cfg['products']}
        eligible={}
        for row in result.get('product_CNs',[]):
            sc=schemes.get(row['scheme']);p=products.get(row['product_id'])
            if not sc or not p or sc.get('deleted_at') or sc.get('mapping_placeholder') or p.get('deleted_at') or 'ABS' not in sc.get('benefits',[]) or sc['season']!=base.get('season') or D(row['regular_net'])<=0:continue
            eligible.setdefault(sc['id'],[]).append(row)
        choices=[{'id':sid,'crop':schemes[sid]['crop'],'segment':schemes[sid]['segment'],'name':schemes[sid]['name'],'packing_kg':schemes[sid]['packing_kg']} for sid in eligible if not crop or schemes[sid]['crop']==crop]
        sources,_,_=payment_work(base)
        for src in sources:
            src['remaining']=src['available']-sum((D(a.get('amount') or 0) for a in base.get('allocations',[]) if a.get('source')==src['id']),Decimal(0))
            src['eligible_schemes']=[s['id'] for s in choices if abs_booking_allowed(src,schemes[s['id']])]
        if options:return {'schemes':choices,'sources':sources,'settings_version':settings['version']}
        if not scheme:
            if len(choices)!=1:raise ValueError('Choose a segment/scheme: this crop has multiple eligible destinations' if choices else 'No eligible net-sold ABS products in this crop')
            scheme=choices[0]['id']
        if not any(s['id']==scheme for s in choices):raise ValueError('Choose an active ABS scheme with eligible net-sold products in this crop')
        sc=schemes[scheme];errors=validate_scheme(sc,True)
        if errors:raise ValueError('Review ABS scheme setup: '+'; '.join(errors))
        src=next((x for x in sources if x['id']==source),None)
        if not src or not abs_booking_allowed(src,sc):raise ValueError('ABS not allowed for this original payment date and scheme')
        approved=removed.get('approved',False) if approved is None and removed else bool(approved)
        remark=removed.get('remark','') if remark is None and removed else (remark or '')
        if src.get('date') and sc.get('abs_end') and src['date']>sc['abs_end'] and not (approved and str(remark).strip()):raise ValueError('Extended ABS needs explicit approval and a remark before distribution')
        amount=D(amount or 0)
        if amount<=0:raise ValueError('Enter a positive ABS amount to distribute')
        if amount>src['remaining']:raise ValueError('ABS distribution exceeds this source’s remaining availability after old dues and other splits')
        rows=sorted(eligible[scheme],key=lambda x:x['product_id'])
        allocated={w['product_id']:D(w['allocated']) for c in result.get('CNs',[]) if c['scheme']==scheme and c['benefit']=='ABS' for w in c['working']}
        caps=[max(Decimal(0),unit_qty(r['regular_net'],sc['unit'],sc['abs_unit'],r['packing_kg'])*D(sc['token'])-allocated.get(r['product_id'],Decimal(0))) for r in rows]
        # Preserve the entered amount's precision and every exact remaining capacity.
        scale=max(2,*[-v.as_tuple().exponent for v in [amount,*caps]])
        factor=10**scale;total=int(amount*factor);limits=[int(v*factor) for v in caps];capacity=sum(limits);budget=min(total,capacity)
        shares=[budget*n//capacity if capacity else 0 for n in limits]
        remainder=budget-sum(shares)
        order=sorted(range(len(rows)),key=lambda i:(-(budget*limits[i]%capacity) if capacity else 0,rows[i]['product_id']))
        for i in order[:remainder]:shares[i]+=1
        # Only money beyond all remaining token capacities is excess. Keep its source/type.
        if total>budget:shares[0]+=total-budget
        group=uuid.uuid4().hex;allocations=[];details=[]
        for i,(row,share) in enumerate(zip(rows,shares)):
            if not share:continue
            value=Decimal(share)/factor
            a={'id':replace_id if not allocations and replace_id else uuid.uuid4().hex,'source':source,'type':'ABS','scheme':scheme,'product':row['product_id'],'amount':plain(value),'remark':remark,'approved':approved,'auto_distribution':{'group':group,'basis':'remaining product token capacity'}}
            allocations.append(a);details.append({'product':row['product'],'product_id':row['product_id'],'net_sold':row['regular_net'],'unit':sc['unit'],'remaining_token_capacity':caps[i],'amount':value,'token_applied':min(value,caps[i]),'excess':max(Decimal(0),value-caps[i])})
        candidate=copy.deepcopy(base);candidate['allocations']+=allocations;validate_input_limits(candidate,settings);after=compute(candidate,settings)
        group_work=next((g for g in after.get('groups',[]) if g['scheme']==scheme),{})
        return {'allocations':allocations,'products':details,'scheme':scheme,'crop':sc['crop'],'scheme_name':sc['name'],'amount':amount,'source':source,'original_date':src['date'],'opening':src['opening'],'replace_id':replace_id,'settings_version':settings['version'],'ABS_CN':next((c['rounded'] for c in after.get('CNs',[]) if c['scheme']==scheme and c['benefit']=='ABS'),Decimal(0)),'CD_CN':next((c['rounded'] for c in after.get('CNs',[]) if c['scheme']==scheme and c['benefit']=='CD'),Decimal(0)),'excess_ABS':group_work.get('excess_ABS',Decimal(0)),'issues':after['issues'],'basis':'Token funding is proportional to remaining product requirements. Any excess is carried on the first displayed product; the engine pools it into this segment’s first configured CD slab.'}
