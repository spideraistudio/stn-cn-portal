"""Explicit Cash quantity booking within Net Rate allocation; no ledger mutation."""
import copy,uuid
from decimal import Decimal,localcontext
from engine import D,compute,effective_settings,payment_work,unit_qty,validate_input_limits,validate_scheme

def preview(record,settings,*,scheme,product,source,amount,supplied,returned='0',replace_id='',deduction_rate=None,remark='',cash_sales_value=None,cash_returns_value=None,billing_split_reason=''):
    with localcontext() as ctx:
        ctx.prec=40
        if record.get('status','draft')!='draft':raise ValueError('Create a draft revision before changing Cash quantity')
        r=copy.deepcopy(record);r.pop('frozen_settings',None);r.pop('result',None)
        cfg=effective_settings(r,settings);sc=next((s for s in cfg['schemes'] if s['id']==scheme),None);p=next((p for p in cfg['products'] if p['id']==product),None)
        if not sc or sc.get('deleted_at') or sc.get('mapping_placeholder') or not sc.get('cash') or not p or p.get('deleted_at') or product not in sc['products'] or p['name'] not in sc['cash']['products']:raise ValueError('Choose an eligible Cash quantity product and scheme')
        if r.get('scheme_overrides',{}).get(p['scheme'],p['scheme'])!=scheme:raise ValueError('Choose the product’s current scheme before booking Cash quantity')
        errors=validate_scheme(sc,True)
        if errors:raise ValueError('Review Cash scheme: '+'; '.join(errors))
        if sc['season']!=r.get('season') or (r.get('scheme_state') or r.get('workbook_scheme_state') or r.get('state')) not in sc['states']:raise ValueError('Cash scheme does not match this state and season')
        old=next((a for a in r.get('allocations',[]) if a['id']==replace_id),None) if replace_id else None
        if replace_id and (not old or old.get('type')!='Cash' or old.get('scheme')!=scheme or old.get('product')!=product):raise ValueError('Choose an existing Cash funding row for this product')
        src=next((s for s in payment_work(r)[0] if s['id']==source),None);cash=sc['cash']
        if not src or not src['date'] or not cash['start']<=src['date']<=cash['end']:raise ValueError('Cash booking must use an eligible original payment date')
        season=next((s for s in cfg['seasons'] if s['name']==r['season']),{})
        if r.get('annual_ledger') and season.get('cutoff') and src['date']>season['cutoff']:raise ValueError('Cash payment is after the calculation cutoff')
        value=D(amount);cs=D(supplied);cr=D(returned or 0)
        if value<=0 or cs<=0:raise ValueError('Enter a positive Cash payment amount and supplied quantity')
        a={'id':replace_id or uuid.uuid4().hex,'scheme':scheme,'product':product,'source':source,'type':'Cash','amount':str(value),'remark':str(remark or '')}
        r['allocations']=[a if x['id']==replace_id else x for x in r.get('allocations',[])] if replace_id else [*r.get('allocations',[]),a]
        split={'scheme':scheme,'product':product,'supplied':str(cs),'returned':str(cr),'deduction_rate':deduction_rate,'remark':str(remark or ''),'cash_sales_value':cash_sales_value,'cash_returns_value':cash_returns_value,'billing_split_reason':str(billing_split_reason or '')}
        r['cash_splits']=[x for x in r.get('cash_splits',[]) if (x['scheme'],x['product'])!=(scheme,product)]+[split]
        validate_input_limits(r,settings)
        funding=sum((D(x['amount']) for x in r['allocations'] if (x.get('type'),x.get('scheme'),x.get('product'))==('Cash',scheme,product)),Decimal(0))
        required=unit_qty(cs,sc['unit'],cash['unit'],p['packing_kg'])*D(cash['advance'])
        if funding<required:raise ValueError('Cash payment after old dues must cover the booked supplied quantity')
        if cr and (deduction_rate in (None,'') or not str(remark or '').strip()):raise ValueError('Cash returns need an explicit deduction rate and remark, including zero')
        after=compute(r,settings)
        row=next((x for x in after.get('product_CNs',[]) if (x['scheme'],x['product_id'])==(scheme,product)),None)
        cn=next((x for x in after.get('CNs',[]) if x['scheme']==scheme and x['benefit']=='Cash '+p['name'] and x['working'].get('product_id')==product),None)
        if not row or not cn:raise ValueError('Review product quantities and invoice values before booking Cash quantity')
        # Do not apply a plan with unresolved Cash financial/traceability errors.
        blocking=('Cash/regular quantity','Cash advance','Cash not enabled','Cash payment/product','Cash deduction','Resolve cash return','Varying invoice rates','Review traceable cash')
        if any(any(i.startswith(k) for k in blocking) for i in after['issues']):raise ValueError('; '.join(i for i in after['issues'] if any(i.startswith(k) for k in blocking)))
        return {'candidate':r,'allocation':a,'split':split,'settings_version':settings['version'],'original_date':src['date'],'cash_supplied':cs,'cash_returned':cr,'cash_net':cs-cr,'regular_net':row['regular_net'],'total_net':row['net_sold'],'unit':sc['unit'],'funding':funding,'required_advance':required,'Cash_CN':cn['rounded'],'issues':after['issues']}
